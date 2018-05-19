ADD_CASE_URL = 'https://my.uscis.gov/account/onboarding/track/new';
HOME_URL = 'https://my.uscis.gov/account/applicant';

var btn = document.createElement("BUTTON");
var t = document.createTextNode("Check");
btn.appendChild(t);
document.body.appendChild(btn);
btn.addEventListener('click', () => {
  var authenticity_token = document.head.querySelector("[name=csrf-token]").content;
  var data = {
    id: 3,
    operationName: 'ElisCaseQuery',
    variables: {
      receiptNumber: "WAC1814451112",
      icamId:"90ab0b21-7e1b-45aa-9b98-99073aa66cc6",
      isElisCase: false
    }
  }
  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/account/graphql');
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.setRequestHeader("x-csrf-token", authenticity_token);
  xhr.onload = function () {
      console.log(xhr.responseText);
  };
  xhr.send(JSON.stringify(data));
});
