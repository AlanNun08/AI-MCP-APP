// GENTLE CACHE CLEAR FOR BUILDYOURSMARTCART.COM (NO RELOAD)
// Copy and paste this script into your browser console on buildyoursmartcart.com

console.log('🧹 Starting gentle cache clear (no reload)...');

(async function gentleCacheClear() {
    try {
        // 1. Clear all service worker caches
        if ('caches' in window) {
            const cacheNames = await caches.keys();
            console.log(`Found ${cacheNames.length} caches to clear:`, cacheNames);
            
            await Promise.all(
                cacheNames.map(cacheName => {
                    console.log('🗑️ Clearing cache:', cacheName);
                    return caches.delete(cacheName);
                })
            );
            console.log('✅ All caches cleared');
        }
        
        // 2. Clear localStorage and sessionStorage
        const localStorageKeys = Object.keys(localStorage);
        const sessionStorageKeys = Object.keys(sessionStorage);
        
        console.log('🧹 Clearing localStorage keys:', localStorageKeys);
        localStorage.clear();
        
        console.log('🧹 Clearing sessionStorage keys:', sessionStorageKeys);
        sessionStorage.clear();
        
        console.log('✅ All storage cleared');
        
        // 3. Clear cookies
        const cookies = document.cookie.split(";");
        console.log(`Found ${cookies.length} cookies to clear`);
        
        cookies.forEach(function(c) { 
            const eqPos = c.indexOf("=");
            const name = eqPos > -1 ? c.substr(0, eqPos) : c;
            document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/";
            document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;domain=." + window.location.hostname;
        });
        console.log('✅ All cookies cleared');
        
        // 4. Show success message (NO RELOAD)
        console.log('🎉 GENTLE CACHE CLEAR COMPLETED!');
        console.log('📧 Your login credentials:');
        console.log('   Email: alannunezsilva0310@gmail.com');
        console.log('   Password: password123');
        console.log('🔄 NO RELOAD - You can now try logging in!');
        
        // Show alert without reload
        alert(`✅ CACHE CLEARED SUCCESSFULLY!

🧹 All caches cleared
🧹 All storage cleared  
🧹 All cookies cleared

🔄 NO RELOAD - Page stays loaded with fresh cache.

Try logging in now with:
📧 Email: alannunezsilva0310@gmail.com
🔑 Password: password123

If login still fails, manually refresh the page once (F5).`);
        
        // NO RELOAD - let user try login immediately
        console.log('✅ Ready to login - no reload needed!');
        
    } catch (error) {
        console.error('❌ Cache clear error:', error);
        alert('❌ Cache clear failed. Try manual cache clear (Ctrl+Shift+Delete).');
    }
})();