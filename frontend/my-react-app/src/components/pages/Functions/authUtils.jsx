// authUtils.js


export const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
};

export const isLoggedIn = () => {
    return getCookie('session') !== undefined;
};

// authUtils.js

export const setSessionCookie = (name, value) => {
    document.cookie = `${name}=${value}; path=/`;
  }
  
export const getSessionCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}