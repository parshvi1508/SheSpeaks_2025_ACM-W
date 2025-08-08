require('dotenv').config();
const firebase = require('firebase/compat/app');
require('firebase/compat/firestore');

// --- Your config, using env vars ---
const firebaseConfig = {
    apiKey: process.env.FIREBASE_API_KEY,
    authDomain: process.env.FIREBASE_AUTH_DOMAIN,
    projectId: process.env.FIREBASE_PROJECT_ID,
    storageBucket: process.env.FIREBASE_STORAGE_BUCKET,
    messagingSenderId: process.env.FIREBASE_MESSAGING_SENDER_ID,
    appId: process.env.FIREBASE_APP_ID,
    measurementId: process.env.FIREBASE_MEASUREMENT_ID
  };

firebase.initializeApp(firebaseConfig);
const db = firebase.firestore();

// --- Answer Pools ---
const years = ['1st', '2nd', '3rd', 'Final'];
const courses = ['CSE', 'ECE', 'IT', 'Mechanical', 'Civil', 'Electrical', 'Biotech', 'AI', 'Data Science', 'Physics', 'Mathematics', ''];
const judged_options = ['multiple', 'sometimes', 'not-really', 'cant-say'];
const voice_options = ['heard', 'ignored', 'talked-over', 'depends'];
const stepped_back_options = ['yes', 'no', 'sometimes', 'still-show-up'];
const curfews_options = ['all-the-time', 'sometimes', 'rarely', 'never'];
const help_options = [
  'all-girls-teams',
  'women-mentors',
  'late-night-access',
  'transparent-selections',
  'anonymous-reporting',
  'not-sure'
];
const held_back_report_samples = [
  "Didn't feel safe.",
  "Worried about backlash.",
  "No proof or evidence.",
  "Didn't want to be labeled as 'dramatic'.",
  "It felt too minor to report.",
  "Didn't know the procedure.",
  "Not sure whom to tell.",
  "Thought it wouldn't be taken seriously.",
  "Didn't want to get anyone 'in trouble'.",
  "I froze in the moment.",
  "It felt normal back then.",
  "Feared being judged or blamed.",
  "I was afraid of isolation afterward.",
  "I've seen others silenced.",
  "Didn't want it to affect my career/opportunities.",
  "Thought it was just me.",
  "Mentors advised me not to escalate.",
  "My mental health was already struggling.",
  "People around me normalized it.",
  "Still unsure if it was report-worthy."
];
const one_change_samples = [
  "More women in leadership roles.",
  "Late-night lab and library access.",
  "Mentorship programs by women in industry.",
  "Transparent and inclusive selection criteria.",
  "Curfew-free access for women during events.",
  "Safe, anonymous reporting systems.",
  "More women-only hackathons or idea jams.",
  "More female judges and panelists at events.",
  "Equal sponsorship for all-girls teams.",
  "Awareness sessions on gender bias and harassment.",
  "A buddy system for newcomers to tech events.",
  "Better mental health support.",
  "Training male peers to be better allies.",
  "Funding and showcasing women's projects more.",
  "Strict zero-tolerance policy for harassment.",
  "Inclusive merchandise (T-shirts that fit women!).",
  "Workshops on how to navigate male-dominated spaces.",
  "A space to just vent, laugh, or cry without judgment.",
  "Fewer 'boys club' vibes at events.",
  "Normalizing failure as part of growth for girls too."
];
const advice_samples = [
  "You don’t need to be perfect to start.",
  "Speak up — even if your voice shakes.",
  "Take up space unapologetically.",
  "You're not alone — find your tribe.",
  "It's okay to fail, just keep showing up.",
  "Ask for help — it doesn’t make you weak.",
  "Say yes before you're ready. You’ll learn.",
  "Take credit for your work — loudly.",
  "Don’t shrink yourself to fit in.",
  "You deserve to be in every room you walk into.",
  "Don’t compare your beginning to someone else's middle.",
  "Silence isn’t strength — your voice is.",
  "Back other women — sisterhood is power.",
  "You can lead *and* be kind. Don’t pick.",
  "Call out unfairness, even if it’s uncomfortable.",
  "Document things — always. It protects you.",
  "Dare to dream bigger than the system allows.",
  "Your intuition is a superpower. Trust it.",
  "Learn. Unlearn. Relearn. And never stop.",
  "Build your own table if none exists.",
  ""
];

// --- Helpers ---
function getRandom(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}
function getRandomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}
function getRandomHelpOptions() {
  const count = getRandomInt(0, 2);
  if (count === 0) return [];
  const shuffled = help_options.slice().sort(() => 0.5 - Math.random());
  return shuffled.slice(0, count);
}
function generateEntry() {
  return {
    year: getRandom(years),
    course: getRandom(courses),
    judged: getRandom(judged_options),
    voice: getRandom(voice_options),
    'stepped-back': getRandom(stepped_back_options),
    curfews: getRandom(curfews_options),
    'boys-club': getRandomInt(1, 5),
    'equal-chances': getRandomInt(1, 5),
    'safe-supported': getRandomInt(1, 5),
    'held-back': getRandomInt(1, 5),
    'women-mentors': getRandomInt(1, 5),
    'held-back-report': getRandom(held_back_report_samples),
    'one-change': getRandom(one_change_samples),
    help: getRandomHelpOptions(),
    advice: getRandom(advice_samples),
    submittedAt: new Date().toISOString()
  };
}

// --- Batch Insert (Firestore batch limit is 500, keep batch <= 250) ---
async function insertSampleEntries(n = 250) {
  const batchSize = 250;
  let count = 0;
  let batch = db.batch();
  const collectionRef = db.collection('responses');

  for (let i = 0; i < n; i++) {
    const entry = generateEntry();
    const docRef = collectionRef.doc();
    batch.set(docRef, entry);
    count++;
    if (count === batchSize || i === n - 1) {
      await batch.commit();
      console.log(`Inserted ${count} entries`);
      // Reset for next batch if needed
      batch = db.batch();
      count = 0;
    }
  }
  console.log(`All ${n} entries inserted!`);
}

insertSampleEntries().then(() => process.exit());
