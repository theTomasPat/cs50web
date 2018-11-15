var socket;
var chatMsgTemplate;
var dayEnum = {
  0: 'Sun',
  1: 'Mon',
  2: 'Tue',
  3: 'Wed',
  4: 'Thur',
  5: 'Fri',
  6: 'Sat',
};
var autoScroll = true;

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
 * and signing in from login page
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

      // verify the rooms list container has been loaded and fill it
      const eltRoomsList = document.querySelector('#room-list-container');
      if (eltRoomsList) {
        fetchRooms();
      }
      
      // verify the chat container has been loaded and fill it
      const eltChatWindow = document.querySelector('#chat-messages-container');
      if (eltChatWindow) {
        // resize chat-messages-container
        const eltChatApp = document.querySelector('#chat-app')
        const eltChatAppHeightCSS = window.getComputedStyle(eltChatApp, null).getPropertyValue('height');
        const eltChatAppHeight = Number(eltChatAppHeightCSS.substr(0, eltChatAppHeightCSS.length - 2));
        eltChatWindow.style.height = updateElementHeight(
          eltChatAppHeight,
          [document.querySelector('#message-input-container')]
        );

        // render the chat message template
        chatMsgTemplate = Handlebars.compile(document.querySelector('#chat-messages-template').innerHTML);

        // grab the last bunch of messages from the server
        fetchMessages(localStorage.getItem('chatRoom'));

        // add event handler for scrolling the chat messages
        eltChatWindow.onscroll = () => {
          if (eltChatWindow.scrollHeight - eltChatWindow.scrollTop === eltChatWindow.clientHeight) {
            autoScroll = true;
          }
          else {
            autoScroll = false;
          }
        };
      }

      // connect SocketIO to server
      socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
      // once successfully connected...
      socket.on('connect', () => {
        console.log("Successfully connected to websocket!");

        // connect to socket room
        let socketRoom = localStorage.getItem('chatRoom');
        if (socketRoom === null) {
          localStorage.setItem('chatRoom', 'Lobby');
        }

        socket.emit('joinRoom', {
          'currentRoom': localStorage.getItem('chatRoom'),
          'desiredRoom': 'Lobby'
        });

        // Add an event handler for new messages
        socket.on('serverMessage', (data) => {
          console.log("Received new message from server");

          // add new message to chat window
          addMessage(data); 

          scrollChatWindow();
        });

        // Add an event handler for new rooms
        socket.on('serverNewRoom', (data) => {
          // add a listing for the new room in the rooms list
          createRoomLinks([data['roomName']]);
        });

        // TODO: Uncomment once done testing. It just spams the login message
        //socket.emit('login', {'username': localStorage.getItem('username')});
      });
    },
    (rejectedData) => {
      document.querySelector('#content-container').innerHTML = rejectedData;
    }
  );
}

/**
 * Retrieve chat messages from the server
 * addMessage() will be called for each message object that was returned
 * 
 * @param {string} chatRoom chat room to retrieve the messages from
 */
function fetchMessages(chatRoom) {
  // Assign 'Lobby' as a default chat room to grab messages from
  if (chatRoom === null) {
    chatRoom = 'Lobby';
  }

  // Initialize new XMLHttpRequest object
  const contentRequest = new XMLHttpRequest();
  contentRequest.open('GET', `/fetchMessages/${chatRoom}`);

  contentRequest.onload = () => {
    // Grab the response data
    const data = contentRequest.response;

    // verify the request happened successfully
    if (data.success) {
      console.log("Received messages back from the server!");

      // Clear the current messages
      document.querySelector('#chat-messages-container').innerHTML = '';

      // Add a new post for each message object that was returned
      data.messages.forEach(addMessage);
    }
    else {
      // Request couldn't be completed. Let someone know
      console.log("Couldn't retrieve chat messages from server.");
    }
  };

  console.log("Attempting to retrieve messages from the server...");
  contentRequest.responseType = 'json';
  contentRequest.send();
}

/**
 * Request a JSON object from the server containing the list of chat rooms available
 *
 */
function fetchRooms() {
  // Initialize new XMLHttpRequest object
  const contentRequest = new XMLHttpRequest();
  contentRequest.open('GET', '/fetchRooms');

  contentRequest.onload = () => {
    const data = contentRequest.response;

    // verify the request happened successfully
    if (data.success) {
      createRoomLinks(data.rooms);
    }
    else {
      // Request couldn't be completed. Let someone know
      console.log("Couldn't retrieve chat rooms from server.");
    }
  }

  console.log("Attempting to retrieve the list of chat rooms on the server");
  contentRequest.responseType = 'json';
  contentRequest.send();
}

/**
 * Create links for each corresponding chat room
 *
 * @param {Array<String>} rooms list of strings representing the names of the chat rooms to create links for
 */
function createRoomLinks(rooms) {
  if (rooms.length > 0) {
    // get the room list container element
    const eltRoomsList = document.querySelector('#room-list-container');

    if (eltRoomsList) {
      // iterate over list of rooms from received data
      rooms.forEach((val) => {
        // add a list item and link for each entry
        eltLink = document.createElement("a");
        eltLink.href = '';
        eltLink.classList.add('room-list-entry');
        eltLink.dataset.roomName = val;
        eltLink.onclick = handleRoomLink;
        eltLink.innerHTML = val;

        // Add new elements to the UL
        eltRoomsList.appendChild(eltLink);
      });
    }
  }
}

/**
 * Submit a request to the server to add a new chat room
 *
 * @returns {boolean} False to prevent page reloading
 */
function createNewRoom(){
  const eltRoomNameInput = document.querySelector('#new-room-name');

  if (eltRoomNameInput) {
    // grab the name from the text field
    const roomName = eltRoomNameInput.value;
    
    // make sure the name has at least one alphanumeric character
    if (!roomName.match(/[A-Za-z0-9]+/)) return false;

    // send the request to the server
    socket.emit('clientRequestNewRoom', {
      'roomName': roomName
    });

    // reset input field
    eltRoomNameInput.value = '';
  }

  // return false to prevent page reload
  return false;
}

/**
 * Responsible for leaving the current chat room and entering the one supplied by the clicked link
 *
 * @param {MouseEvent} event MouseEvent
 * @returns {Boolean} false to prevent page reloading
 */
function handleRoomLink(event) {
  // within this handler 'this' refers to the Element that was clicked
  const linkRoom = this.dataset.roomName;

  // leave current SocketIO room and join the one from the link
  socket.emit('joinRoom', {
    'currentRoom': localStorage.getItem('chatRoom'),
    'desiredRoom': this.dataset.roomName
  })
  localStorage.setItem('chatRoom', this.dataset.roomName);

  fetchMessages(this.dataset.roomName);

  // prevent page reload
  return false;
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

/**
 * Send a message to the server
 *
 * @returns false - used to prevent the page from reloading because the form was submitted
 */
function sendMessage() {
  // Grab the html element for the message text
  const messageInputField = document.querySelector('#message-input');

  // if that element query didn't return null
  if (messageInputField) {
    // emit a socket event containing necessary message data
    socket.emit('clientMessage', {
      'room': localStorage.getItem('chatRoom'),
      'username': localStorage.getItem('username'),
      'body': messageInputField.value
    });
  }

  // reset message input field
  messageInputField.value = '';

  // prevent page reload
  return false;
}

/**
 * Build and add a chat message element to the chat window.
 * Element will be built using the Handlebars template found in chat.html
 *
 * @param {Object} contents - JS object that must contain keys: timestamp, username, body
 */
function addMessage(contents) {
  const msgDate = new Date(Math.floor(contents['timestamp'] * 1000));
  // convert Date object to a string
  const dateDay = dayEnum[msgDate.getDay()];
  const dateHours = formatHours(msgDate.getHours());
  const dateMinutes = formatMinutes(msgDate.getMinutes());
  const dateStr = `Sent ${dateDay} ${dateHours}:${dateMinutes}`;
  const msgTimestamp = dateStr;
  const msgUsername = contents['username'];
  const msgBody = contents['body'];

  // build message element from compiled template
  const message = chatMsgTemplate({
    'timestamp': msgTimestamp,
    'username': msgUsername,
    'body': msgBody
  });
  console.log(`Adding message {${msgTimestamp}, ${msgUsername}, ${msgBody}}`);

  // add rendered element to the chat message container
  document.querySelector('#chat-messages-container').innerHTML += message;

  scrollChatWindow();
}

/**
 * Return a properly formatted hour value
 * It must be in 12 hr format and 12AM must read as 12, not 0
 *
 * @param {number} hrs hour component of Date object in range [0, 23]
 * @returns {number} hour component of time in range [1, 12]
 */
function formatHours(hrs) {
  if (hrs == 0) {
    return 12;
  }

  return (hrs > 12) ? hrs - 12 : hrs;
}

/**
 * Return a properly formatted string representing minutes
 * The returned string must be zero-padded
 *
 * @param {number} mins Minutes component of Date object in range [0, 59]
 * @returns {string} String representing the minutes component of time from "00" to "59"
 */
function formatMinutes(mins) {
  return (mins < 10) ? `0${mins}` : String(mins);
}

/**
 * Scroll the chat messages window down to the bottom
 *
 */
function scrollChatWindow() {
  eltChatMessagesContainer = document.querySelector('#chat-messages-container');

  if (eltChatMessagesContainer && autoScroll) {
    eltChatMessagesContainer.scrollTop = eltChatMessagesContainer.scrollHeight;
  }
}