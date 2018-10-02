// Once the document has been loaded, do stuff
document.addEventListener('DOMContentLoaded', () => {
  // set the content-container div's height
  document.querySelector('#content-container').style.height = updateElementHeight(
    window.innerHeight,
    [document.querySelector('#page-header')]
  );

  // add event listener for window resizing
  window.onresize = () => {
    // Resize main content container
    document.querySelector('#content-container').style.height = updateElementHeight(
      window.innerHeight,
      [document.querySelector('#page-header')]
    );
    
    // If it exists, resize the chat messages container
    const eltChatWindow = document.querySelector('#chat-messages-container');
    if (eltChatWindow) {
      const eltChatApp = document.querySelector('#chat-app')
      const eltChatAppHeightCSS = window.getComputedStyle(eltChatApp, null).getPropertyValue('height');
      const eltChatAppHeight = Number(eltChatAppHeightCSS.substr(0, eltChatAppHeightCSS.length - 2));

      // resize chat messages container
      eltChatWindow.style.height = updateElementHeight(
        eltChatAppHeight,
        [document.querySelector('#message-input-container')]
      );
    }
  };

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
  fetchChatApp();

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

/**
 * Wrapper for the fetchHTML function
 * used specifically for loading the chat app
 *
 */
function fetchChatApp() {
  fetchHTML("chat").then(
    (resolvedData) => {
      document.querySelector('#content-container').innerHTML = resolvedData;
      
      // resize chat-messages-container
      const eltChatWindow = document.querySelector('#chat-messages-container');
      if (eltChatWindow) {
        const eltChatApp = document.querySelector('#chat-app')
        const eltChatAppHeightCSS = window.getComputedStyle(eltChatApp, null).getPropertyValue('height');
        const eltChatAppHeight = Number(eltChatAppHeightCSS.substr(0, eltChatAppHeightCSS.length - 2));

        // do the actual resizing
        eltChatWindow.style.height = updateElementHeight(
          eltChatAppHeight,
          [document.querySelector('#message-input-container')]
        );
      }
    },
    (rejectedData) => {
      document.querySelector('#content-container').innerHTML = rejectedData;
    }
  );
}

/**
 * Return a CSS value string representing a number of pixels to resize the given element by.
 * The value is calculated by subtracting the sum of the height of the "sibling" elements from
 * the provided "max" value.
 *
 * @param {Number} max Number of pixels to be used as the maximum bound
 * @param {Array<HTMLElement>} siblings Array of elements whose heights will be summed and subtracted from "max"
 * @return {String} CSS value string in the form of "Npx" where N is the calculated pixel height for the given element
 */
function updateElementHeight(max, siblings) {
  let siblingHeights = 0;

  // map/reduce siblings array
  // map array to get computed style of each sibling element, extract height value, convert to Number
  // reduce siblings array to add all the sibling heights together
  siblingHeights = siblings.map((val) => {
    const eltHeightCSS = window.getComputedStyle(val, null).getPropertyValue('height');
    const eltHeight = Number(eltHeightCSS.substr(0, eltHeightCSS.length - 2));
    return eltHeight;
  }).reduce((acc, currVal) => {
    return acc + currVal;
  }, 0);

  return String(max - siblingHeights) + "px";
}