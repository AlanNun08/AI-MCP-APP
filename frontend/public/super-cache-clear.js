// SUPER AGGRESSIVE CACHE CLEAR FOR BUILDYOURSMARTCART.COM
// Copy and paste this ENTIRE script into your browser console on buildyoursmartcart.com

console.log('🚨 STARTING SUPER AGGRESSIVE CACHE CLEAR...');

(async function superAggressiveCacheClear() {
    try {
        // Step 1: Unregister ALL service workers
        console.log('🔧 Step 1: Unregistering all service workers...');
        if ('serviceWorker' in navigator) {
            const registrations = await navigator.serviceWorker.getRegistrations();
            console.log(`Found ${registrations.length} service workers`);
            
            for (let registration of registrations) {
                console.log('Unregistering service worker:', registration.scope);
                await registration.unregister();
            }
            console.log('✅ All service workers unregistered');
        }
        
        // Step 2: Delete ALL caches
        console.log('🗑️ Step 2: Deleting all caches...');
        if ('caches' in window) {
            const cacheNames = await caches.keys();
            console.log(`Found ${cacheNames.length} caches:`, cacheNames);
            
            await Promise.all(
                cacheNames.map(async (cacheName) => {
                    console.log('Deleting cache:', cacheName);
                    return caches.delete(cacheName);
                })
            );
            console.log('✅ All caches deleted');
        }
        
        // Step 3: Clear ALL browser storage
        console.log('🧹 Step 3: Clearing all storage...');
        
        // Clear localStorage
        const localStorageKeys = Object.keys(localStorage);
        console.log('Clearing localStorage keys:', localStorageKeys);
        localStorage.clear();
        
        // Clear sessionStorage
        const sessionStorageKeys = Object.keys(sessionStorage);
        console.log('Clearing sessionStorage keys:', sessionStorageKeys);
        sessionStorage.clear();
        
        // Clear IndexedDB
        if (window.indexedDB) {
            try {
                const databases = await indexedDB.databases();
                console.log(`Found ${databases.length} IndexedDB databases`);
                
                for (let db of databases) {
                    console.log('Deleting IndexedDB:', db.name);
                    indexedDB.deleteDatabase(db.name);
                }
            } catch (e) {
                console.log('IndexedDB clearing not supported');
            }
        }
        
        // Step 4: Clear ALL cookies
        console.log('🍪 Step 4: Clearing all cookies...');
        const cookies = document.cookie.split(";");
        console.log(`Found ${cookies.length} cookies`);
        
        cookies.forEach(function(c) { 
            const eqPos = c.indexOf("=");
            const name = eqPos > -1 ? c.substr(0, eqPos) : c;
            document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/";
            document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;domain=." + window.location.hostname;
            console.log('Cleared cookie:', name.trim());
        });
        
        // Step 5: Force browser to ignore cache
        console.log('⚡ Step 5: Setting no-cache headers...');
        
        // Override fetch to always use no-cache
        const originalFetch = window.fetch;
        window.fetch = function(url, options = {}) {
            options.headers = {
                ...options.headers,
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            };
            options.cache = 'no-store';
            return originalFetch(url, options);
        };
        
        // Step 6: Show success and force reload
        console.log('🎉 SUPER AGGRESSIVE CACHE CLEAR COMPLETED!');
        console.log('📧 Your login credentials:');
        console.log('   Email: alannunezsilva0310@gmail.com');
        console.log('   Password: password123');
        console.log('🔄 FORCING HARD RELOAD...');
        
        // Show alert before reload
        alert(`✅ SUPER AGGRESSIVE CACHE CLEAR COMPLETED!

📧 Email: alannunezsilva0310@gmail.com
🔑 Password: password123

🔄 Page will now HARD RELOAD with no cache.
After reload, try logging in immediately!`);
        
        // Force the hardest possible reload
        window.location.href = window.location.href + '?cache_bust=' + Date.now();
        
    } catch (error) {
        console.error('❌ Error during cache clear:', error);
        alert('❌ Error during cache clear. Check console for details.');
    }
})();

// Also add this backup method
setTimeout(() => {
    console.log('🔄 BACKUP RELOAD TRIGGERED');
    window.location.reload(true);
}, 5000);