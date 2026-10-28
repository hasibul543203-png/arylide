(function(){
  const dictionaries = {
    bn: {
      appName: "ARYLIDE Holdings",
      welcome: "আপনার পরবর্তী ঠিকানা",
      welcomeSub: "প্রজেক্ট দেখুন, বিস্তারিত জানুন, অথবা মিটিং বুক করুন।",
      home: "হোম", projects: "প্রজেক্ট", sectors: "সেক্টর", meetings: "মিটিং", videos: "ভিডিও", more: "আরও",
      bookMeeting: "📅 মিটিং বুক করুন", login: "লগইন", signup: "অ্যাকাউন্ট তৈরি করুন", logout: "লগআউট", myMeetings: "আমার মিটিং",
      switchLanguage: "English", featured: "ফিচার্ড প্রজেক্ট", allProjects: "সব প্রজেক্ট", sectorProjects: "সেক্টর {sector}-এর প্রজেক্ট",
      chooseSector: "সেক্টর বেছে নিন", noSectorProjects: "এই সেক্টরে এখনো কোনো ARYLIDE প্রজেক্ট প্রকাশিত হয়নি।",
      details: "বিস্তারিত দেখুন", projectDetails: "প্রজেক্টের বিস্তারিত", location: "লোকেশন", price: "মূল্য", amenities: "সুবিধাসমূহ",
      gallery: "গ্যালারি", map: "ম্যাপ", openMap: "ম্যাপে দেখুন", contactForPrice: "বর্তমান মূল্য জানতে যোগাযোগ করুন",
      bookThisProject: "এই প্রজেক্টে মিটিং বুক করুন", updates: "আমাদের প্রজেক্ট আপডেট", facebook: "Facebook", linkedin: "LinkedIn", x: "X / Twitter",
      projectVideos: "প্রজেক্ট ভিডিও", watchVideo: "ভিডিও দেখুন", noVideos: "ভিডিও শিগগির যোগ হবে।",
      calculator: "ইনভেস্টমেন্ট ক্যালকুলেটর", area: "এরিয়া (SFT)", pricePerSft: "প্রতি SFT মূল্য (৳)", downPayment: "ডাউন পেমেন্ট (%)", months: "মাস", growth: "বার্ষিক সম্ভাব্য বৃদ্ধি (%)",
      totalPrice: "মোট মূল্য", downAmount: "ডাউন পেমেন্ট", remaining: "অবশিষ্ট", monthly: "মাসিক কিস্তি", futureValue: "৩ বছর পর সম্ভাব্য মূল্য", profit: "সম্ভাব্য বৃদ্ধি",
      calculatorAssumption: "ক্যালকুলেশনটি আপনার দেওয়া মূল্য ও বৃদ্ধির হার অনুযায়ী।",
      bookTitle: "মিটিং বুক করুন", step1: "তারিখ ও সময় নির্বাচন", step2: "আপনার তথ্য", previousMonth: "আগের মাস", nextMonth: "পরের মাস", selectDate: "একটি তারিখ বেছে নিন", selectTime: "সময় বেছে নিন", booked: "বুকড", offDay: "বন্ধ", available: "খালি",
      name: "নাম", mobile: "মোবাইল", email: "ইমেইল", projectInterested: "আগ্রহের প্রজেক্ট", message: "মেসেজ", confirmMeeting: "✅ মিটিং কনফার্ম করুন", bookingSummary: "আপনার মিটিং", meetingPlace: "লোকেশন", meetingOfficeDefault: "আমাদের গুলশান অফিস / অনলাইন Zoom",
      chooseDateFirst: "আগে তারিখ ও সময় নির্বাচন করুন।", meetingSuccess: "✅ মিটিং বুক হয়েছে! আমরা আপনাকে {time}-এর মধ্যে কল করব।", meetingSavedLocal: "মিটিংটি এই ডিভাইসে সংরক্ষিত হয়েছে।",
      noMeetings: "এখনো কোনো মিটিং বুক করা হয়নি।", cancelMeeting: "মিটিং বাতিল", reschedule: "পুনরায় সময় নিন", pending: "অপেক্ষমাণ", confirmed: "নিশ্চিত", completed: "সম্পন্ন", cancelled: "বাতিল",
      loginTitle: "আপনার অ্যাকাউন্টে লগইন করুন", signupTitle: "ARYLIDE-তে অ্যাকাউন্ট তৈরি করুন", password: "পাসওয়ার্ড", phone: "মোবাইল নম্বর", googleContinue: "Google দিয়ে চালিয়ে যান", sendOtp: "OTP পাঠান", verifyOtp: "OTP যাচাই করুন", otp: "SMS OTP", authNotConfigured: "Firebase এখনো সেটআপ করা হয়নি। মালিক Firebase তথ্য যোগ করলে লগইন চালু হবে।", authError: "লগইন সম্পন্ন হয়নি। তথ্য যাচাই করে আবার চেষ্টা করুন।", authLoading: "Firebase সংযোগ হচ্ছে…",
      emailPassword: "ইমেইল ও পাসওয়ার্ড", create: "অ্যাকাউন্ট তৈরি করুন", haveAccount: "আগে থেকেই অ্যাকাউন্ট আছে?", needAccount: "অ্যাকাউন্ট নেই?", back: "ফিরে যান", close: "বন্ধ করুন", continue: "চালিয়ে যান", save: "সংরক্ষণ", cancel: "বাতিল",
      landInquiry: "জমির মালিকের অনুসন্ধান", referral: "রেফারেল", companyInfo: "কোম্পানি তথ্য", websiteInfo: "সম্পূর্ণ তথ্য দেখুন", admin: "অ্যাডমিন", explore: "প্রজেক্ট দেখুন", status: "স্ট্যাটাস", bookingOngoing: "বুকিং চলছে", sold: "বিক্রি সম্পন্ন", detailsOnRequest: "বিস্তারিত জানতে যোগাযোগ করুন", conceptImage: "কনসেপ্ট ছবি",
      stats: { projects: "প্রজেক্ট", completed: "সম্পন্ন প্রজেক্ট", happy_clients: "সন্তুষ্ট ক্লায়েন্ট", years_trust: "বছরের আস্থা", area_built: "নির্মিত মোট এলাকা (SFT)", vision_sqft: "স্কয়ার ফিটে ভিশন" },
      project: {
        "arylide-purbasha": { description: "ARYLIDE-এর প্রকাশিত ক্যাম্পেইনে দেখানো সম্পন্ন প্রজেক্ট।", status: "ক্যাম্পেইনে সম্পন্ন হিসেবে দেখানো", location: "গ্রিন মডেল টাউন · ঢাকা", amenities: "বিস্তারিত জানতে যোগাযোগ করুন" },
        "sky-high-living": { description: "‘Reach New Heights of Comfort’ ক্যাম্পেইনে দেখানো আবাসিক প্রজেক্ট।", status: "আবাসিক ক্যাম্পেইন", location: "ARYLIDE Residences", amenities: "যাচাইকৃত সুবিধার তথ্য জানতে যোগাযোগ করুন" },
        "uttara-signature-address": { description: "প্রদত্ত টিজারে ‘Coming Soon’ উল্লেখ আছে।", status: "শিগগির আসছে", location: "উত্তরা · ঢাকা", amenities: "তথ্য প্রকাশিত হলে এখানে দেখানো হবে" },
        "arylide-breezy": { description: "ARYLIDE-এর ওয়েবসাইটে ফিচার্ড প্রজেক্ট হিসেবে তালিকাভুক্ত।", status: "প্রজেক্টের তথ্য জানতে যোগাযোগ করুন", location: "বসুন্ধরা R/A", amenities: "তথ্য প্রকাশিত হলে এখানে দেখানো হবে" },
        "nisorgo": { description: "ARYLIDE-এর ওয়েবসাইটে ফিচার্ড প্রজেক্ট হিসেবে তালিকাভুক্ত।", status: "প্রজেক্টের তথ্য জানতে যোগাযোগ করুন", location: "বসুন্ধরা R/A", amenities: "তথ্য প্রকাশিত হলে এখানে দেখানো হবে" },
        "jolshiri-land": { description: "জলশিরি আবাসনে জমির মালিকদের সঙ্গে অংশীদারত্বের জন্য ARYLIDE-এর ক্যাম্পেইন।", status: "জমির মালিক অংশীদারত্ব", location: "জলশিরি আবাসন", amenities: "জমির তথ্য নিয়ে কথা বলতে যোগাযোগ করুন" },
        "ashiyana": { description: "লেকভিউ ও ব্রিজ সংলগ্ন, কর্নার প্লট, স্কুল ও মসজিদ সন্নিকটে।", status: "বুকিং তথ্য জানতে যোগাযোগ করুন", location: "সেক্টর ১৪ · জলশিরি আবাসন", amenities: "নিকটবর্তী: লেক, ব্রিজ, স্কুল ও মসজিদ" },
        "bashundhara-tower": { description: "ক্লায়েন্ট-প্রদত্ত ব্রিফে বাণিজ্যিক প্রজেক্ট হিসেবে তালিকাভুক্ত।", status: "বাণিজ্যিক", location: "বসুন্ধরা R/A · ঢাকা", amenities: "যাচাইকৃত তথ্য জানতে যোগাযোগ করুন" },
        "uttara-heights": { description: "ক্লায়েন্ট-প্রদত্ত ব্রিফে মিশ্র-ব্যবহার প্রজেক্ট হিসেবে তালিকাভুক্ত।", status: "মিশ্র-ব্যবহার", location: "উত্তরা · ঢাকা", amenities: "যাচাইকৃত তথ্য জানতে যোগাযোগ করুন" }
      }
    },
    en: {
      appName: "ARYLIDE Holdings",
      welcome: "Your next address",
      welcomeSub: "Explore projects, learn more, or book a meeting.",
      home: "Home", projects: "Projects", sectors: "Sectors", meetings: "Meetings", videos: "Videos", more: "More",
      bookMeeting: "📅 Book a Meeting", login: "Log in", signup: "Create account", logout: "Log out", myMeetings: "My meetings",
      switchLanguage: "বাংলা", featured: "Featured projects", allProjects: "All projects", sectorProjects: "Projects in Sector {sector}",
      chooseSector: "Choose a sector", noSectorProjects: "No ARYLIDE project has been published for this sector yet.",
      details: "View details", projectDetails: "Project details", location: "Location", price: "Price", amenities: "Amenities",
      gallery: "Gallery", map: "Map", openMap: "Open map", contactForPrice: "Contact us for current pricing",
      bookThisProject: "Book a meeting about this project", updates: "Our project updates", facebook: "Facebook", linkedin: "LinkedIn", x: "X / Twitter",
      projectVideos: "Project videos", watchVideo: "Watch video", noVideos: "Videos will be added soon.",
      calculator: "Investment calculator", area: "Area (SFT)", pricePerSft: "Price per SFT (৳)", downPayment: "Down payment (%)", months: "Months", growth: "Potential annual growth (%)",
      totalPrice: "Total price", downAmount: "Down payment", remaining: "Remaining", monthly: "Monthly instalment", futureValue: "Potential value in 3 years", profit: "Potential increase",
      calculatorAssumption: "Calculated from the price and growth rate you enter.",
      bookTitle: "Book a meeting", step1: "Select date & time", step2: "Your details", previousMonth: "Previous month", nextMonth: "Next month", selectDate: "Choose a date", selectTime: "Choose a time", booked: "Booked", offDay: "Closed", available: "Available",
      name: "Name", mobile: "Mobile", email: "Email", projectInterested: "Project of interest", message: "Message", confirmMeeting: "✅ Confirm meeting", bookingSummary: "Your meeting", meetingPlace: "Location", meetingOfficeDefault: "Our Gulshan office / online Zoom",
      chooseDateFirst: "Select a date and time first.", meetingSuccess: "✅ Meeting booked! We will call you by {time}.", meetingSavedLocal: "The meeting was saved on this device.",
      noMeetings: "You have no meetings booked yet.", cancelMeeting: "Cancel meeting", reschedule: "Reschedule", pending: "Pending", confirmed: "Confirmed", completed: "Completed", cancelled: "Cancelled",
      loginTitle: "Log in to your account", signupTitle: "Create your ARYLIDE account", password: "Password", phone: "Mobile number", googleContinue: "Continue with Google", sendOtp: "Send OTP", verifyOtp: "Verify OTP", otp: "SMS OTP", authNotConfigured: "Firebase is not configured yet. Login will be available after the owner adds Firebase settings.", authError: "Could not complete sign-in. Check your details and try again.", authLoading: "Connecting to Firebase…",
      emailPassword: "Email and password", create: "Create account", haveAccount: "Already have an account?", needAccount: "New here?", back: "Go back", close: "Close", continue: "Continue", save: "Save", cancel: "Cancel",
      landInquiry: "Landowner enquiry", referral: "Referral", companyInfo: "Company information", websiteInfo: "Full company information", admin: "Admin", explore: "Explore projects", status: "Status", bookingOngoing: "Booking information", sold: "Sold", detailsOnRequest: "Contact us for details", conceptImage: "Concept image",
      stats: { projects: "Projects", completed: "Completed projects", happy_clients: "Happy clients", years_trust: "Years of trust", area_built: "Total area built (SFT)", vision_sqft: "Vision in square feet" },
      project: {
        "arylide-purbasha": { description: "A completed project featured in ARYLIDE's published campaign.", status: "Shown as completed in campaign", location: "Green Model Town · Dhaka", amenities: "Contact us for details" },
        "sky-high-living": { description: "Residential project featured in the ‘Reach New Heights of Comfort’ campaign.", status: "Residential campaign", location: "ARYLIDE Residences", amenities: "Contact us for verified amenities" },
        "uttara-signature-address": { description: "The supplied teaser says ‘Coming Soon.’", status: "Coming soon", location: "Uttara · Dhaka", amenities: "Details will be shown when published" },
        "arylide-breezy": { description: "Listed as a featured project on ARYLIDE's website.", status: "Contact us for project information", location: "Bashundhara R/A", amenities: "Details will be shown when published" },
        "nisorgo": { description: "Listed as a featured project on ARYLIDE's website.", status: "Contact us for project information", location: "Bashundhara R/A", amenities: "Details will be shown when published" },
        "jolshiri-land": { description: "ARYLIDE campaign for landowner partnerships at Jolshiri Abashon.", status: "Landowner partnership", location: "Jolshiri Abashon", amenities: "Contact us to discuss a land opportunity" },
        "ashiyana": { description: "Adjacent to the lake and bridge; corner plot, near a school and mosque.", status: "Contact us about booking", location: "Sector 14 · Jolshiri Abashon", amenities: "Nearby: lake, bridge, school and mosque" },
        "bashundhara-tower": { description: "Listed as a commercial project in the client-provided brief.", status: "Commercial", location: "Bashundhara R/A · Dhaka", amenities: "Contact us for verified details" },
        "uttara-heights": { description: "Listed as a mixed-use project in the client-provided brief.", status: "Mixed use", location: "Uttara · Dhaka", amenities: "Contact us for verified details" }
      }
    }
  };
  let current = localStorage.getItem('aryl_language') || 'bn';
  if (!dictionaries[current]) current = 'bn';
  function value(path, params) {
    const lang = dictionaries[current] || dictionaries.bn;
    let result = path.split('.').reduce((node, part) => node && node[part], lang);
    if (result == null) result = path.split('.').reduce((node, part) => node && node[part], dictionaries.en);
    if (typeof result !== 'string') return path;
    return result.replace(/\{(\w+)\}/g, (_, key) => params && params[key] != null ? String(params[key]) : `{${key}}`);
  }
  function setLanguage(lang) {
    current = dictionaries[lang] ? lang : 'bn';
    try { localStorage.setItem('aryl_language', current); } catch (_) {}
    document.documentElement.lang = current;
    window.dispatchEvent(new CustomEvent('aryl-language-change', { detail: { language: current } }));
  }
  window.ARYLIDE_I18N = { dictionaries, t: value, get language() { return current; }, setLanguage };
})();
