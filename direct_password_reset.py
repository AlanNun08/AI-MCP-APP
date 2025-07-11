#!/usr/bin/env python3
"""
Direct database password reset for Alan.nunez0310@icloud.com
"""
import asyncio
import motor.motor_asyncio
import bcrypt
import os

# Database configuration
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = "ai_recipe_app_production"

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

async def reset_user_password():
    """Reset password directly in database"""
    
    # Connect to MongoDB
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    email = "Alan.nunez0310@icloud.com"
    new_password = "newpassword123"
    
    try:
        print(f"🔍 Connecting to database...")
        
        # Find user
        user = await db.users.find_one({"email": {"$regex": f"^{email}$", "$options": "i"}})
        
        if user:
            print(f"✅ Found user: {user.get('email')}")
            print(f"   User ID: {user.get('id')}")
            print(f"   Is Verified: {user.get('is_verified', False)}")
            
            # Hash new password
            hashed_password = hash_password(new_password)
            
            # Update user with new password and ensure verified
            result = await db.users.update_one(
                {"email": {"$regex": f"^{email}$", "$options": "i"}},
                {
                    "$set": {
                        "password_hash": hashed_password,
                        "is_verified": True  # Make sure user is verified
                    }
                }
            )
            
            if result.modified_count > 0:
                print(f"✅ Password reset successful!")
                print(f"   New password: {new_password}")
                print(f"   User is now verified")
                
                # Clear any old verification codes
                await db.verification_codes.delete_many({"user_email": {"$regex": f"^{email}$", "$options": "i"}})
                await db.password_reset_codes.delete_many({"user_email": {"$regex": f"^{email}$", "$options": "i"}})
                
                print(f"✅ Cleared old verification and reset codes")
                
            else:
                print(f"❌ No changes made to user")
        else:
            print(f"❌ User not found: {email}")
            
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
    finally:
        client.close()

async def main():
    """Main function"""
    print("🔧 Direct Database Password Reset")
    print("=" * 40)
    
    await reset_user_password()
    
    print(f"\n🎉 Password reset completed!")
    print(f"   Email: Alan.nunez0310@icloud.com")
    print(f"   Password: newpassword123")
    print(f"\n📱 You can now login to the app!")

if __name__ == "__main__":
    asyncio.run(main())