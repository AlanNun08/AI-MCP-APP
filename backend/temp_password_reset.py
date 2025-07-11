#!/usr/bin/env python3
"""
Temporary Password Reset Script for Production
Usage: python3 temp_password_reset.py
"""

import os
import asyncio
import bcrypt
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def reset_password_for_user(email: str, new_password: str):
    """Reset password for a specific user"""
    try:
        # Connect to database
        client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
        db = client[os.environ.get('DB_NAME', 'ai_recipe_app_production')]
        
        # Hash the new password
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Update user's password
        result = await db.users.update_one(
            {'email': email.lower()},
            {'$set': {'password_hash': password_hash}}
        )
        
        if result.modified_count > 0:
            print(f"✅ Password successfully updated for {email}")
            print(f"New password: {new_password}")
            return True
        else:
            print(f"❌ User {email} not found")
            return False
            
    except Exception as e:
        print(f"❌ Error resetting password: {str(e)}")
        return False

async def main():
    """Main function to reset password"""
    email = "alannunezsilva0310@gmail.com"
    new_password = "TempPassword123!"
    
    print(f"🔄 Resetting password for {email}...")
    success = await reset_password_for_user(email, new_password)
    
    if success:
        print("\n" + "="*50)
        print("✅ PASSWORD RESET SUCCESSFUL!")
        print(f"Email: {email}")
        print(f"New Password: {new_password}")
        print("="*50)
        print("\nYou can now login to your deployed website with these credentials.")
        print("Remember to change your password after logging in!")
    else:
        print("\n❌ Password reset failed. Please check the logs above.")

if __name__ == "__main__":
    asyncio.run(main())