// Once the document has been loaded, do stuff
document.addEventListener('DOMContentLoaded', () => {

  // grab the user's username from local storage
  var username = localStorage.getItem('username');

  // if user is not logged in, request login page html from server
  if (username == null) {
    console.log("user is not logged in, initializing request for login form");

    fetchLoginForm();
    
    // update the user-info field in the page header
    updateUserInfo(false);
  }
  else {
    // user is logged in, make request for chat application
    login();

    // update the user-info field in the page header
    updateUserInfo(true);
  }
});

/**
 * Handle swapping the Login and Logout links in the header
 *
 * @param {boolean} loggedIn
 */
function updateUserInfo(loggedIn) {
  const logoutMsg = `Logged in as ${localStorage.getItem('username')}: <a href="" onclick="return logout();">Logout</a>`;
  document.querySelector('#user-info').innerHTML = (loggedIn) ? logoutMsg : "Login";
}

/**
 * Handle clicking the login link in the header
 *
 * @return {boolean} false
 */
function login() {
  if (localStorage.getItem('username') === null) {
    console.log(`Logging in with username ${document.querySelector('#login-username').value}`);
    localStorage.setItem('username', String(document.querySelector('#login-username').value));
  }
  updateUserInfo(true);

  // grab the html to make up the chat app
  fetchHTML("chat").then(
    (resolvedData) => {
      document.querySelector('#content-container').innerHTML = resolvedData;
    },
    (rejectedData) => {
      document.querySelector('#content-container').innerHTML = rejectedData;
    }
  );
  return false;
}

/**
 * Handle clicking the logout link in the header
 *
 * @return {boolean} false
 */
function logout() {
  console.log("Logging out");
  localStorage.removeItem('username');
  updateUserInfo(false);
  fetchLoginForm();
  return false;
}

/**
 * Function to fetch html resources from the server via XMLHttpRequest
 *
 * @param {string} resource
 * @returns {Promise} Promise object
 */
function fetchHTML(resource) {
  return new Promise((resolve, reject) => {
    // build XMLHttpRequest object
    const contentRequest = new XMLHttpRequest();
    contentRequest.open('GET', `/fetchHTML/${resource}`);

    // callback for when we receive data back from server
    contentRequest.onload = () => {
      console.log(`Received data back from the server for request "${resource}"`);
      const data = contentRequest.response;

      if (data.success) {
        console.log(`Request for "${resource}" was a success`);
        resolve(data.data);
      }
      else {
        console.log(`Request for "${resource}" failed`);
        reject(`<p>Error loading resource: ${resource}</p>`);
      }

    };

    // send request
    console.log(`Sending XMLHttpRequest for "${resource}"...`);
    contentRequest.responseType = 'json';
    contentRequest.send();
  });
}

/**
 * Wrapper for the fetchHTML function
 * used specifically for loading the login form
 *
 */
function fetchLoginForm(){
  fetchHTML("login").then(
    (resolvedData) => {
      document.querySelector('#content-container').innerHTML = resolvedData;
    },
    (rejectedData) => {
      document.querySelector('#content-container').innerHTML = rejectedData;
    }
  );
}