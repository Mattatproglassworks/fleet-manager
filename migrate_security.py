"""
Database migration script to add security fields to User model
Run this once to upgrade the database schema
"""
from app import app, db, User
from sqlalchemy import text

def migrate_database():
    with app.app_context():
        try:
            # Check if columns already exist
            inspector = db.inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('user')]
            
            print("📊 Existing columns:", existing_columns)
            
            # Add new columns if they don't exist
            with db.engine.connect() as conn:
                if 'is_active' not in existing_columns:
                    print("➕ Adding 'is_active' column...")
                    conn.execute(text('ALTER TABLE user ADD COLUMN is_active BOOLEAN DEFAULT 1'))
                    conn.commit()
                
                if 'failed_login_attempts' not in existing_columns:
                    print("➕ Adding 'failed_login_attempts' column...")
                    conn.execute(text('ALTER TABLE user ADD COLUMN failed_login_attempts INTEGER DEFAULT 0'))
                    conn.commit()
                
                if 'locked_until' not in existing_columns:
                    print("➕ Adding 'locked_until' column...")
                    conn.execute(text('ALTER TABLE user ADD COLUMN locked_until DATETIME'))
                    conn.commit()
                
                if 'last_login_ip' not in existing_columns:
                    print("➕ Adding 'last_login_ip' column...")
                    conn.execute(text('ALTER TABLE user ADD COLUMN last_login_ip VARCHAR(45)'))
                    conn.commit()
            
            # Create indexes for performance
            print("🔍 Creating indexes...")
            with db.engine.connect() as conn:
                try:
                    conn.execute(text('CREATE INDEX IF NOT EXISTS idx_user_username ON user(username)'))
                    conn.execute(text('CREATE INDEX IF NOT EXISTS idx_user_email ON user(email)'))
                    conn.commit()
                except Exception as e:
                    print(f"⚠️  Index creation skipped (may already exist): {e}")
            
            # Update all existing users to be active
            print("✅ Setting all existing users to active...")
            User.query.update({User.is_active: True, User.failed_login_attempts: 0})
            db.session.commit()
            
            print("✅ Migration completed successfully!")
            print("🔐 Security features enabled:")
            print("   - Account locking after 5 failed attempts")
            print("   - IP-based rate limiting")
            print("   - Session security")
            print("   - Password strength validation")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    migrate_database()
