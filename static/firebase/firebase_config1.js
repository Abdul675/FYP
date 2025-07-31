// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.10.0/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/9.10.0/firebase-auth.js";

// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyAq6SMcIJDXbe9OZSe71bQiSmfVsiqlYrU",
  authDomain: "signuplogin-e9d31.firebaseapp.com",
  databaseURL: "https://signuplogin-e9d31-default-rtdb.firebaseio.com/",
  projectId: "signuplogin-e9d31",
  storageBucket: "signuplogin-e9d31.firebasestorage.app",
  messagingSenderId: "76564232814",
  appId: "1:76564232814:web:699bf6e4718f9b494d047f"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication
const auth = getAuth(app);

export { auth };