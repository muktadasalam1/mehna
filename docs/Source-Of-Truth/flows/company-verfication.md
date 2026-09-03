# company verfication flow 

when the company is created it's status is unverfied .

---
## first step : Company action
the company will make a request to the server for verfication they might provide some goverment verfication .
the endpoint that the company will reach should **NOT** have an admin permission .
the endpoint that the company will reach should do the following :
1- create a pending verfication request (the pending verfication request will be storied in the db).
2- return a "A varification request has been sand, please wait for admin apporval ", to the comany .


## second step : Admin action
the admin will open a page "verfication request" the page will contact the "list Verfication request endpoint" this page will view the requests as a list (table) .

when the admin clicks on one of the idems in that table a request will send to "get verfication request" (which will return the verfication request information).

In that instant the admin has a couple of action to do:\
1- Approve the request (by sending a request to "Approve verfication request endpoint" (which is an admin endpoiont) and the admin should provide the id of the verfication request(the frontend may do that automaticlly and not a manual input by the admin) ).

2- Reject the request (by sending a request to "Reject Verfication request endpoint"(which is an admin endpoint) and the admin should provide the id of the verfication request(the frontend may do that automaticlly and not a manual input by the admin) and the reason for the rejection )

- **After approval** the comany status should be verified (meaning the frontend should display a varified tag beside the comany name).

- **After Rejection** the comany status shouldn't change (staied at **Not Verified**), but the varification request should be audited with the reason and time stamp .



## thired step : Server action
**notification** the server should send an email or an in-app notificaiton to notify the company about the verfication , or rejection(with the reason).
