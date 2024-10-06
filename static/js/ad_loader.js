
function loadAds() {
    document.querySelectorAll('.ad-placeholder').forEach(placeholder => {
        const adData = JSON.parse(placeholder.dataset.ad);
        let adContent = '';

        if (adData.type === 'google') {
            // Google Ads এর জন্য স্ক্রিপ্ট ইনজেক্ট করুন
            const script = document.createElement('script');
            script.innerHTML = adData.content;
            placeholder.appendChild(script);
        } else {
            if (adData.content.includes('<img')) {
                // ইমেজ এড
                adContent = `<a href="${adData.url}" target="_blank">${adData.content}</a>`;
            } else if (adData.url) {
                // টেক্সট লিংক
                adContent = `<a href="${adData.url}" target="_blank">${adData.title}</a>`;
            } else {
                // সাধারণ কন্টেন্ট
                adContent = adData.content;
            }
            placeholder.innerHTML = adContent;
        }

        // এডের লোডিং এফেক্ট
        placeholder.style.opacity = '0';
        setTimeout(() => {
            placeholder.style.transition = 'opacity 0.5s';
            placeholder.style.opacity = '1';
        }, Math.random() * 1000); // র‍্যান্ডম ডিলে
    });
}

// পেজ লোড হওয়ার পর এডগুলি লোড করুন
window.addEventListener('load', loadAds);
