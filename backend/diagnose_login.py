#!/usr/bin/env python
"""Diagnostic script to check database and users"""
import asyncio
from database import connect_to_mongo, get_database
from utils.auth import verify_password

async def diagnose():
    print("🔍 DIAGNOSING LOGIN ISSUE")
    print("=" * 50)
    
    # Connect to database
    try:
        await connect_to_mongo()
        print("✅ MongoDB Connection: SUCCESS")
    except Exception as e:
        print(f"❌ MongoDB Connection: FAILED - {e}")
        return
    
    db = get_database()
    
    # Check users collection
    try:
        user_count = await db.users.count_documents({})
        print(f"✅ Users in database: {user_count}")
        
        if user_count == 0:
            print("⚠️  NO USERS FOUND! Database is empty!")
            print("   Solution: Restart backend to seed demo data")
            return
        
        # List all users
        users = await db.users.find({}).to_list(10)
        print("\n📋 DEMO USERS:")
        for user in users:
            email = user.get("email")
            role = user.get("role")
            has_pwd = "password_hash" in user
            print(f"  • {email} ({role}) - Password hash: {'✅' if has_pwd else '❌'}")
        
        # Test login with employee account
        print("\n🧪 TESTING LOGIN WITH: employee@sifsentinel.demo / Employee@123")
        test_user = await db.users.find_one({"email": "employee@sifsentinel.demo"})
        
        if not test_user:
            print("❌ User not found in database!")
            return
        
        pwd_hash = test_user.get("password_hash")
        if not pwd_hash:
            print("❌ User has no password hash!")
            return
        
        # Test password verification
        is_valid = verify_password("Employee@123", pwd_hash)
        print(f"✅ Password verification: {'PASS' if is_valid else 'FAIL'}")
        
        if not is_valid:
            print("⚠️  Password verification failed!")
            print("   This means the password doesn't match the hash")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(diagnose())
