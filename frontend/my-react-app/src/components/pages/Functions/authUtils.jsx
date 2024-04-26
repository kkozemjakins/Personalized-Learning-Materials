// authUtils.js
export const getUserInfo = () => {
    const userEmail = sessionStorage.getItem("user_email");
    const userId = sessionStorage.getItem("user_id");
    const userRole = sessionStorage.getItem("user_role");
    return { userEmail, userId, userRole };
};
