// Complete cache clearing and refresh script
// Run this in your browser console on the deployed site

(async function clearEverything() {
    console.log('🔄 Starting complete cache clear...');
    
    // 1. Clear all service worker caches
    if ('caches' in window) {
        const cacheNames = await caches.keys();
        console.log('📦 Found caches:', cacheNames);
        
        await Promise.all(
            cacheNames.map(cacheName => {
                console.log('🗑️ Deleting cache:', cacheName);
                return caches.delete(cacheName);
            })
        );
        console.log('✅ All service worker caches cleared');
    }
    
    // 2. Unregister all service workers
    if ('serviceWorker' in navigator) {
        const registrations = await navigator.serviceWorker.getRegistrations();
        console.log('🔧 Found service workers:', registrations.length);
        
        for (let registration of registrations) {
            await registration.unregister();
            console.log('❌ Unregistered service worker');
        }
        console.log('✅ All service workers unregistered');
    }
    
    // 3. Clear all localStorage
    console.log('🗑️ Clearing localStorage...');
    localStorage.clear();
    console.log('✅ localStorage cleared');
    
    // 4. Clear all sessionStorage
    console.log('🗑️ Clearing sessionStorage...');
    sessionStorage.clear();
    console.log('✅ sessionStorage cleared');
    
    // 5. Clear IndexedDB
    if (window.indexedDB) {
        try {
            const databases = await indexedDB.databases();
            console.log('🗄️ Found IndexedDB databases:', databases.length);
            
            for (let db of databases) {
                indexedDB.deleteDatabase(db.name);
                console.log('🗑️ Deleted database:', db.name);
            }
            console.log('✅ All IndexedDB databases cleared');
        } catch (e) {
            console.log('⚠️ IndexedDB clearing not supported in this browser');
        }
    }
    
    // 6. Clear cookies for this domain
    document.cookie.split(";").forEach(function(c) { 
        document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/"); 
    });
    console.log('✅ Cookies cleared');
    
    // 7. Show success message
    console.log('🎉 COMPLETE CACHE CLEAR SUCCESSFUL!');
    console.log('📝 NEW LOGIN CREDENTIALS:');
    console.log('📧 Email: alannunezsilva0310@gmail.com');
    console.log('🔑 Password: password123');
    console.log('🔄 Reloading page in 3 seconds...');
    
    // 8. Alert user
    alert('✅ All caches cleared!\n\n📧 Email: alannunezsilva0310@gmail.com\n🔑 Password: password123\n\n🔄 Page will reload now...');
    
    // 9. Force reload
    setTimeout(() => {
        window.location.reload(true);
    }, 3000);
})();