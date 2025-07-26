-- Telegram Jobs Bot Database Schema for Supabase
-- This file contains all the necessary tables and functions for the bot

-- Enable Row Level Security
ALTER DATABASE postgres SET "app.jwt_secret" TO 'your-jwt-secret-here';

-- Create users table
CREATE TABLE IF NOT EXISTS bot_users (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    language_code VARCHAR(10),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create user preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES bot_users(telegram_id) ON DELETE CASCADE,
    language_preference VARCHAR(20) DEFAULT 'both', -- 'arabic', 'global', 'both'
    location_preference VARCHAR(20) DEFAULT 'both', -- 'specific', 'remote', 'both'
    preferred_country VARCHAR(100),
    skills TEXT[], -- Array of skills
    notification_frequency INTEGER DEFAULT 1, -- 0=on-demand, 1=once, 2=twice, 3=three times
    notification_times TIME[] DEFAULT ARRAY['09:00'::TIME], -- Array of notification times
    onboarding_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Create jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    company VARCHAR(255),
    description TEXT,
    location VARCHAR(255),
    job_type VARCHAR(50), -- 'full-time', 'part-time', 'contract', 'remote', etc.
    salary_range VARCHAR(100),
    apply_url TEXT NOT NULL,
    source VARCHAR(100), -- 'google_jobs', 'remoteok', 'wuzzuf', etc.
    source_job_id VARCHAR(255), -- Original job ID from source
    skills_required TEXT[], -- Array of required skills
    is_remote BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    link_status VARCHAR(20) DEFAULT 'unknown', -- 'working', 'broken', 'unknown'
    link_checked_at TIMESTAMP WITH TIME ZONE,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(source, source_job_id) -- Prevent duplicates from same source
);

-- Create job notifications table (tracks which jobs were sent to which users)
CREATE TABLE IF NOT EXISTS job_notifications (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES bot_users(telegram_id) ON DELETE CASCADE,
    job_id BIGINT REFERENCES jobs(id) ON DELETE CASCADE,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notification_type VARCHAR(50) DEFAULT 'daily', -- 'daily', 'manual', 'urgent'
    is_clicked BOOLEAN DEFAULT FALSE,
    clicked_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(user_id, job_id) -- Prevent sending same job to same user twice
);

-- Create job opinions table (for storing community opinions about jobs/companies)
CREATE TABLE IF NOT EXISTS job_opinions (
    id BIGSERIAL PRIMARY KEY,
    job_id BIGINT REFERENCES jobs(id) ON DELETE CASCADE,
    company VARCHAR(255),
    source VARCHAR(50), -- 'reddit', 'twitter', 'linkedin'
    opinion_text TEXT,
    sentiment VARCHAR(20), -- 'positive', 'negative', 'neutral'
    author VARCHAR(255),
    source_url TEXT,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create search logs table (for analytics and improving search)
CREATE TABLE IF NOT EXISTS search_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES bot_users(telegram_id) ON DELETE CASCADE,
    search_type VARCHAR(50), -- 'daily_auto', 'manual', 'skills_based'
    search_parameters JSONB, -- Store search criteria as JSON
    results_count INTEGER DEFAULT 0,
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create bot statistics table
CREATE TABLE IF NOT EXISTS bot_statistics (
    id BIGSERIAL PRIMARY KEY,
    date DATE DEFAULT CURRENT_DATE,
    total_users INTEGER DEFAULT 0,
    active_users INTEGER DEFAULT 0,
    jobs_scraped INTEGER DEFAULT 0,
    notifications_sent INTEGER DEFAULT 0,
    search_requests INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(date)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_bot_users_telegram_id ON bot_users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_jobs_source ON jobs(source);
CREATE INDEX IF NOT EXISTS idx_jobs_scraped_at ON jobs(scraped_at);
CREATE INDEX IF NOT EXISTS idx_jobs_is_active ON jobs(is_active);
CREATE INDEX IF NOT EXISTS idx_jobs_skills ON jobs USING GIN(skills_required);
CREATE INDEX IF NOT EXISTS idx_job_notifications_user_id ON job_notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_job_notifications_sent_at ON job_notifications(sent_at);
CREATE INDEX IF NOT EXISTS idx_job_opinions_job_id ON job_opinions(job_id);
CREATE INDEX IF NOT EXISTS idx_search_logs_user_id ON search_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_search_logs_executed_at ON search_logs(executed_at);

-- Create function to update updated_at column automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE OR REPLACE TRIGGER update_bot_users_updated_at 
    BEFORE UPDATE ON bot_users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE OR REPLACE TRIGGER update_user_preferences_updated_at 
    BEFORE UPDATE ON user_preferences 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE OR REPLACE TRIGGER update_jobs_updated_at 
    BEFORE UPDATE ON jobs 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Create function to match jobs with user preferences
CREATE OR REPLACE FUNCTION match_jobs_for_user(user_telegram_id BIGINT, limit_count INTEGER DEFAULT 5)
RETURNS TABLE (
    job_id BIGINT,
    title VARCHAR(500),
    company VARCHAR(255),
    location VARCHAR(255),
    apply_url TEXT,
    match_score INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        j.id as job_id,
        j.title,
        j.company,
        j.location,
        j.apply_url,
        (
            -- Score based on skills match
            CASE 
                WHEN up.skills && j.skills_required THEN 3
                ELSE 0
            END +
            -- Score based on location preference
            CASE 
                WHEN up.location_preference = 'remote' AND j.is_remote THEN 2
                WHEN up.location_preference = 'specific' AND j.location ILIKE '%' || up.preferred_country || '%' THEN 2
                WHEN up.location_preference = 'both' THEN 1
                ELSE 0
            END +
            -- Score based on recency
            CASE 
                WHEN j.scraped_at > NOW() - INTERVAL '24 hours' THEN 1
                ELSE 0
            END
        ) as match_score
    FROM jobs j
    CROSS JOIN user_preferences up
    WHERE up.user_id = user_telegram_id
        AND j.is_active = TRUE
        AND j.link_status != 'broken'
        AND NOT EXISTS (
            SELECT 1 FROM job_notifications jn 
            WHERE jn.user_id = user_telegram_id AND jn.job_id = j.id
        )
    ORDER BY match_score DESC, j.scraped_at DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Create function to get user statistics
CREATE OR REPLACE FUNCTION get_user_stats(user_telegram_id BIGINT)
RETURNS TABLE (
    total_notifications INTEGER,
    jobs_clicked INTEGER,
    last_notification TIMESTAMP WITH TIME ZONE,
    registration_date TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(jn.id)::INTEGER as total_notifications,
        COUNT(CASE WHEN jn.is_clicked THEN 1 END)::INTEGER as jobs_clicked,
        MAX(jn.sent_at) as last_notification,
        MIN(bu.created_at) as registration_date
    FROM bot_users bu
    LEFT JOIN job_notifications jn ON bu.telegram_id = jn.user_id
    WHERE bu.telegram_id = user_telegram_id
    GROUP BY bu.telegram_id;
END;
$$ LANGUAGE plpgsql;

-- Enable Row Level Security on all tables
ALTER TABLE bot_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_opinions ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_logs ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (users can only access their own data)
CREATE POLICY "Users can view their own data" ON bot_users
    FOR ALL USING (telegram_id = (current_setting('request.jwt.claims', true)::json->>'telegram_id')::bigint);

CREATE POLICY "Users can view their own preferences" ON user_preferences
    FOR ALL USING (user_id = (current_setting('request.jwt.claims', true)::json->>'telegram_id')::bigint);

CREATE POLICY "Users can view all jobs" ON jobs FOR SELECT USING (true);

CREATE POLICY "Users can view their own notifications" ON job_notifications
    FOR ALL USING (user_id = (current_setting('request.jwt.claims', true)::json->>'telegram_id')::bigint);

CREATE POLICY "Users can view all opinions" ON job_opinions FOR SELECT USING (true);

CREATE POLICY "Users can view their own search logs" ON search_logs
    FOR ALL USING (user_id = (current_setting('request.jwt.claims', true)::json->>'telegram_id')::bigint);

-- Insert some sample data for testing
INSERT INTO bot_users (telegram_id, username, first_name, language_code) VALUES
(123456789, 'testuser1', 'Ahmed', 'ar'),
(987654321, 'testuser2', 'Sara', 'ar')
ON CONFLICT (telegram_id) DO NOTHING;

INSERT INTO user_preferences (user_id, language_preference, location_preference, preferred_country, skills, notification_frequency, onboarding_completed) VALUES
(123456789, 'both', 'remote', NULL, ARRAY['Python', 'Web Development', 'Machine Learning'], 1, true),
(987654321, 'arabic', 'specific', 'Saudi Arabia', ARRAY['Graphic Design', 'UI/UX', 'Adobe Creative Suite'], 2, true)
ON CONFLICT (user_id) DO NOTHING;

-- Insert sample jobs
INSERT INTO jobs (title, company, description, location, job_type, apply_url, source, source_job_id, skills_required, is_remote) VALUES
('Python Developer', 'Tech Company', 'Looking for experienced Python developer', 'Remote', 'full-time', 'https://example.com/job1', 'remoteok', 'job1', ARRAY['Python', 'Django', 'PostgreSQL'], true),
('مطور ويب', 'شركة التقنية', 'مطلوب مطور ويب متخصص في React', 'الرياض، السعودية', 'دوام كامل', 'https://example.com/job2', 'wuzzuf', 'job2', ARRAY['React', 'JavaScript', 'Node.js'], false),
('UI/UX Designer', 'Design Studio', 'Creative UI/UX designer needed', 'Dubai, UAE', 'contract', 'https://example.com/job3', 'bayt', 'job3', ARRAY['Figma', 'Adobe XD', 'UI/UX'], false)
ON CONFLICT (source, source_job_id) DO NOTHING;

-- Update bot statistics
INSERT INTO bot_statistics (date, total_users, active_users, jobs_scraped, notifications_sent)
VALUES (CURRENT_DATE, 2, 2, 3, 0)
ON CONFLICT (date) DO UPDATE SET
    total_users = EXCLUDED.total_users,
    active_users = EXCLUDED.active_users,
    jobs_scraped = EXCLUDED.jobs_scraped;

COMMENT ON TABLE bot_users IS 'Stores basic information about Telegram bot users';
COMMENT ON TABLE user_preferences IS 'Stores user preferences for job matching and notifications';
COMMENT ON TABLE jobs IS 'Stores all scraped job listings from various sources';
COMMENT ON TABLE job_notifications IS 'Tracks which jobs have been sent to which users';
COMMENT ON TABLE job_opinions IS 'Stores community opinions and reviews about jobs and companies';
COMMENT ON TABLE search_logs IS 'Logs all search activities for analytics';
COMMENT ON TABLE bot_statistics IS 'Daily statistics about bot usage and performance';

