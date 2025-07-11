#!/usr/bin/env python3
"""
Test password hashing and verification
"""
import bcrypt
import asyncio
import motor.motor_asyncio

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

async def test_password_for_alan():
    """Test password hashing for Alan's account"""
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['ai_recipe_app_production']
    
    # Test password
    test_password = 'newpassword123'
    
    # Get Alan's user data
    user = await db.users.find_one({'email': 'alan.nunez0310@icloud.com'})
    if user:
        print(f"Found user: {user.get('email')}")
        stored_hash = user.get('password_hash', '')
        print(f"Stored hash length: {len(stored_hash)}")
        print(f"Stored hash starts with: {stored_hash[:20]}...")
        
        # Test verification
        is_valid = verify_password(test_password, stored_hash)
        print(f"Password verification: {is_valid}")
        
        if not is_valid:
            print("❌ Password verification failed, creating new hash...")
            
            # Create new hash
            new_hash = hash_password(test_password)
            print(f"New hash length: {len(new_hash)}")
            print(f"New hash starts with: {new_hash[:20]}...")
            
            # Test new hash
            test_new = verify_password(test_password, new_hash)
            print(f"New hash verification: {test_new}")
            
            if test_new:
                # Update in database
                result = await db.users.update_one(
                    {'email': 'alan.nunez0310@icloud.com'},
                    {'$set': {'password_hash': new_hash}}
                )
                print(f"✅ Updated password hash in database: {result.modified_count > 0}")
        else:
            print("✅ Password verification successful!")
    
    client.close()

async def main():
    print("🔐 Testing Password Hashing for Alan's Account")
    print("=" * 50)
    
    await test_password_for_alan()
    
    print("\n🧪 Testing both accounts...")
    
    # Test both accounts
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['ai_recipe_app_production']
    
    emails = ['alan.nunez0310@icloud.com', 'alannunezsilva0310@gmail.com']
    password = 'newpassword123'
    
    for email in emails:
        user = await db.users.find_one({'email': email})
        if user:
            print(f"\n📧 Testing {email}:")
            
            # Create proper hash
            new_hash = hash_password(password)
            
            # Update database
            result = await db.users.update_one(
                {'email': email},
                {'$set': {'password_hash': new_hash, 'is_verified': True}}
            )
            
            # Verify it works
            test_verify = verify_password(password, new_hash)
            print(f"   Hash updated: {result.modified_count > 0}")
            print(f"   Verification test: {test_verify}")
            
    client.close()

if __name__ == "__main__":
    asyncio.run(main())