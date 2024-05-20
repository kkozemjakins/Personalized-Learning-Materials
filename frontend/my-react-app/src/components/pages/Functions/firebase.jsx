// firebase.js

import firebase from 'firebase/compat/app';
import 'firebase/compat/auth';


const firebaseConfig = {
    apiKey: "AIzaSyCjeOJdQt7FGL51O8usJ4gjgaDj__yGhLc",
    authDomain: "eduaisystem.firebaseapp.com",
    databaseURL: "https://eduaisystem-default-rtdb.europe-west1.firebasedatabase.app",
    projectId: "eduaisystem",
    storageBucket: "eduaisystem.appspot.com",
    messagingSenderId: "727514708805",
    appId: "1:727514708805:web:b854dec280d1b06cc15c2c",
    measurementId: "G-D8E5Z7T8J2"
  };

  if (!firebase.apps.length) {
    firebase.initializeApp(firebaseConfig);
  }

export const auth = firebase.auth();

export default firebase;