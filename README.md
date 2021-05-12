# Philosopher

Philosopher is the back-end for the Kwot app. It handles creation of all Quotes and Meanings. Submissions for Quote of the Day, voting on Quote of the Day, as well as relationships between users (friendships).

## API

You must be authorized to access all endpoints. More information on authorization will be available soon.

- [Quotes and Meanings](#quotes-and-meanings)
- [Friends and friend requests](#friends-and-friend-requests)
- [Today functionality](#today-functionality)



### Quotes and Meanings

[Go back to top](#api)

Users can write as many Quotes as they want. Each user on the platform is only allowed to submit one Meaning per Quote. A Quote is meant to be some sort of meaningful text, and a Meaning is meant to describe the readers interpretation of the Quote.

- Quotes
  - [Get all Quotes](#get-all-quotes)
  - [Create a Quote](#create-a-quote)
  - [Get one Quote](#get-one-quote)
  - [Disown a Quote](#disown-a-quote)
- Meanings
  - [Get all Meanings for a Quote](#get-all-meanings-for-a-quote)
  - [Create a Meaning for a Quote](#create-a-meaning-for-a-quote)


#### Get all Quotes

[Go back to header](#quotes-and-meanings)

List all Quotes that a user has written. You must be friends with a user in order to use this endpoint, and you must specify the user ID of the user whos Quotes you are trying to see through a query parameter. See options for more details.

##### Endpoint

`GET /quotes`

##### Options

| Option | Type | Description |
| --- | --- | --- |
| `user_id` | Query parameter | **Required**, the ID of the user whos Quotes you would like to get |

##### Responses

| Response | Description |
| --- | --- |
| `400` | "Missing required query parameter." You didn't include the required `user_id` query parameter. |
| `403` | "You are not friends with this user." You must be friends with a user in order to see their Quotes. |
| `200` | "Success." See example below.

##### Example responses

```json
{
  "message": "Success.",
  "data": [
    {
      "id": 172,
      "body": "Kwot is the most useless platform on the internet",
      "published": "2021-05-05 22:05:03.029577+00:00"
    }
  ]
}
```


#### Create a Quote

[Go back to header](#quotes-and-meanings)

Create a new Quote. Specify the text for the Quote using the "body" field in the request body.

##### Endpoint

`POST /Quotes`

##### Options

| Option | Type | Description |
| --- | --- | --- |
| `body` | Request body field | **Required**, the text for the Quote. Must contain fewer than 140 characters. |

##### Responses

| Response | Description |
| --- | --- |
| `400` | "Missing request body." You didn't include the request body. |
| `400` | "Missing body field in request body." You must specify the value for "body" in the request body. |
| `400` | "Invalid body failed validation." The body of the Quote likely contains more than 140 characters.
| `201` | "Success." The Quote has been created. |

##### Example responses

```json
{
  "message": "Success.",
  "data": {
    "id": 173,
    "body": "I'm so good at writing Quotes.",
    "published": "2021-05-05 22:05:03.029577+00:00"
  }
}
```


#### Get one Quote

[Go back to header](#quotes-and-meanings)

Get a specific Quote. You don't need to be friends with the author to be able to get their Quote in this way.

##### Endpoint

`GET /quotes/{quote_id}`

##### Options

| Option | Type | Description |
| --- | --- | --- |
| `quote_id` | Path parameter | **Required**, the ID of the Quote you would like to get |

##### Responses

| Response | Description |
| --- | --- |
| `404` | "Not found." No Quote matching the specified `quote_id` exists. |
| `200` | "Success." See example below.

##### Example responses

```json
{
  "message": "Success.",
  "data": {
    "id": 172,
    "body": "Kwot is the most useless platform on the internet",
    "published": "2021-05-05 22:05:03.029577+00:00"
  }
}
```


#### Disown a Quote

[Go back to header](#quotes-and-meanings)

Disown a specific Quote. You can't delete a Quote but you can remove your association with the Quote so the author will be written as "anonyomus." This endpoint is only available to authors of the Quote.

##### Endpoint

`DELETE /quotes/{quote_id}`

##### Options

| Option | Type | Description |
| --- | --- | --- |
| `quote_id` | Path parameter | **Required**, the ID of the Quote you would like to disown. |

##### Responses

| Response | Description |
| --- | --- |
| `404` | "Not found." No Quote matching the specified `quote_id` exists. |
| `403` | "You cannot disown a Quote that is not yours." You have to be the author of the quote in order to disown it. |
| `200` | "Success." This endpoint doesn't return any data. See example below.

##### Example responses

```json
{
  "message": "Success."
}
```


#### Get all Meanings for a Quote

[Go back to header](#quotes-and-meanings)

Get all the Meanings for a specified Quote. Only the author of the Quote is allowed to query this endpoint.

##### Endpoint

`GET /quotes/{quote_id}/meanings`

##### Options

| Option | Type | Description |
| --- | --- | --- |
| `quote_id` | Path parameter | **Required**, the ID of the Quote whos Meanings you would like to get |

##### Responses

| Response | Description |
| --- | --- |
| `404` | "Quote does not exist." No Quote with the specified `quote_id` could be found. |
| `403` | "Only the author is permitted to see Meanings for this Quote." You can only view all Meanings for a Quote if you are the author of the Quote. |
| `200` | "Success." See example below.

##### Example responses

```json
{
  "message": "Success.",
  "data": [
    {
      "id": 3298,
      "body": "The author feels much pain. They are deeply disappointed in French Toast Crunch.",
      "published": "2021-05-05 22:05:03.029577+00:00"
    }
  ]
}
```


#### Create a Meaning for a Quote

[Go back to header](#quotes-and-meanings)

Create a new Meaning. Specify the text for the Meaning using the "body" field in the request body. Each user is only allowed to create at most one Meaning for each Quote.

##### Endpoint

`POST /quotes/{quote_id}/meanings`

##### Options

| Option | Type | Description |
| --- | --- | --- |
| `quote_id` | Path parameter | **Required**, the ID of the Quote for which you would like to create a Meaning. |
| `body` | Request body field | **Required**, the text for the Meaning. Must contain fewer than 240 characters. |

##### Responses

| Response | Description |
| --- | --- |
| `404` | "Quote does not exist." No Quote with the specified `quote_id` could be found. |
| `403` | "You cannot write Meanings for your own Quote." It's as simple as it says. |
| `403` | "You are not permitted to create a Meaning for this Quote." You can only create a Meaning for a Quote if you are friends with the author or if the Quote is currently on your voting ballot. |
| `403` | "You have already submitted a Meaning for this Quote." Each user is only allowed to submit one Meaning per Quote.
| `400` | "Missing request body." You didn't include the request body. |
| `400` | "Missing body field in request body." You must specify the value for "body" in the request body. |
| `400` | "Invalid body failed validation." The body of the Meaning likely contains more than 240 characters. |
| `201` | "Success." The Meaning has been created. |

##### Example responses

```json
{
  "message": "Success.",
  "data": {
    "id": 173,
    "body": "I'm so good at writing Meanings.",
    "published": "2021-05-05 22:05:03.029577+00:00"
  }
}
```



### Friends and friend requests

[Go back to top](#api)

Some CRUD related endpoints are dependent on users being friends. For this reason there are a few endpoints to handle sending friend requests and dealing with friends.

- Friends
  - [Get all friends of an author](#get-all-friends-of-an-author)
  - [Accept a friend request](#accept-a-friend-request)
  - [Remove a friend](#remove-a-friend)
- Requests
  - [Get all friend requests](#get-all-friend-requests)
  - [Send a friend request](#send-a-friend-request)
  - [Dismiss a friend request](#dismiss-a-friend-request)


#### Get all friends of an author

[Go back to header](#friends-and-friend-requests)

See all of a users friends. You must be friends with the user to query this endpoint.

##### Endpoint

`GET /authors/{user_id}/friends`

##### Options

| Option | Type | Description |
| --- | --- | --- |
| `user_id` | Path parameter | **Required**, the user to get friends of. |

##### Responses

| Response | Description |
| --- | --- |
| `403` | "You are not friends with this user." You must be friends with the user whos friends you are trying to see. |
| `200` | "Success." See example below. |

##### Example responses

```json
{
  "message": "Success.",
  "data": [
    {
      "user_id": "auth0|60933a869201390068ec9895",
      "nickname": "matootie",
      "picture": "https://cdn.auth0.com/avatars/ma.png"
    }
  ]
}
```


#### Accept a friend request

[Go back to header](#friends-and-friend-requests)

This endpoint is grouped under "friends" because it's effectively creating a new friend, but is dependent on there having been an existing request.

##### Endpoint

`POST /authors/{user_id}/friends`

##### Options

| Option | Type | Description |
| --- | --- | --- |
| `user_id` | Path parameter | **Required**, the ID of the user to "create" a friend for. |
| `request_id` | Body field | **Required**, the ID of the user whos friend request you are accepting. |

##### Responses

| Response | Description |
| --- | --- |
| `403` | "You are not allowed to perform this action." You cannot accept requests on someone elses behalf. |
| `400` | "Missing request body." You didn't include the request body. |
| `400` | "Missing value for request_id in request body." You need to specify the user ID who's request you are trying to accept. |
| `400` | "You cannot be friends with yourself." The message says it all. |
| `400` | "The specified user has not sent you a friend request." The user ID you specified has not sent you a request and therefore you cannot add them as a friend. |
| `200` | "Success." See example below. |

##### Example responses

```json
{
  "message": "Success."
}
```


#### Remove a friend

[Go back to header](#friends-and-friend-requests)

Remove a user as a friend.

##### Endpoint

`DELETE /authors/{user_id}/friends/{friend_id}`

##### Options

| Option | Type | Description |
| --- | --- | --- |
| `user_id` | Path parameter | **Required**, the user ID of the user who wants to remove a friend. |
| `friend_id` | Path parameter | **Required**, the user to remove from your friends list. |

##### Responses

| Response | Description |
| --- | --- |
| `403` | "You are not allowed to perform this action." You cannot remove friends on someone elses behalf. |
| `400` | "The specified user is not your friend." You are trying to remove someone as a friend who wasn't your friend to begin with. |
| `200` | "Success." See example below. |

##### Example responses

```json
{
  "message": "Success."
}
```


#### Get all friend requests

[Go back to header](#friends-and-friend-requests)

See all of your friend requests. You are only allowed to see *your* friend requests and no one elses.

##### Endpoint

`GET /authors/{user_id}/requests`

##### Options

| Option | Type | Description |
| --- | --- | --- |
| `user_id` | Path parameter | **Required**, the user to get requests of. |

##### Responses

| Response | Description |
| --- | --- |
| `403` | "You are not allowed to view this users requests." Only the recipient of the request is able to view. |
| `200` | "Success." See example below. |

##### Example responses

```json
{
  "message": "Success.",
  "data": [
    {
      "user_id": "auth0|60933a869201390068ec9895",
      "nickname": "matootie",
      "picture": "https://cdn.auth0.com/avatars/ma.png"
    }
  ]
}
```


#### Send a friend request

[Go back to header](#friends-and-friend-requests)

Send a friend request to a specific user.

##### Endpoint

`PUT /authors/{recipient_id}/requests/{user_id}`

##### Options

| Option | Type | Description |
| --- | --- | --- |
| `recipient_id` | Path parameter | **Required**, the ID of the user who you want to request friendship from. |
| `user_id` | Path parameter | **Required**, the ID of the user sending the request. |

##### Responses

| Response | Description |
| --- | --- |
| `403` | "You cannot send a friend request on someone elses behalf." You can only send friend requests on behalf of yourself. |
| `400` | "You cannot create a request to yourself." You can't be friends with yourself. |
| `400` | "You are already friends." The user you are trying to send a friend request to is already your friend. |
| `201` | "Both have requested and thus are now friends." You sent a request to a user who has already requested to be friends with you. You get immediately promoted to friends. |
| `200` | "Success." See example below. |

##### Example responses

```json
{
  "message": "Success."
}
```


#### Dismiss a friend request

[Go back to header](#friends-and-friend-requests)

Remove a request to be friends. Only the recipient of the request can query this endpoint.

##### Endpoint

`DELETE /authors/{recipient_id}/requests/{user_id}`

##### Options

| Option | Type | Description |
| --- | --- | --- |
| `recipient_id` | Path parameter | **Required**, the user ID of the user who has received the request. |
| `user_id` | Path parameter | **Required**, the user ID of the user whos request is to be dismissed. |

##### Responses

| Response | Description |
| --- | --- |
| `403` | "You cannot decline a friend request on someone elses behalf." You can only decline friend requests on your own behalf. |
| `400` | "You do not have a friend request from this user." The user whos request you are trying to remove has never sent you a friend request. |
| `200` | "Success." See example below. |

##### Example responses

```json
{
  "message": "Success."
}
```



### Today functionality

[Go back to top](#api)

The today service of the API allows users to retrieve Quotes to vote on, to submit votes, to submit their own Quotes for Quote of the Day, and to view the Quote of the Day through history. Documentation will be available soon.

- [Get the Quote of the Day](#get-the-quote-of-the-day)
- [Get Quotes to vote on](#get-quotes-to-vote-on)
- [Vote on a Quote](#vote-on-a-quote)
- [Submit a Quote for Quote of the Day](#submit-a-quote-for-quote-of-the-day)


#### Get the Quote of the Day

[Go back to header](#today-functionality)

Get the Quote of the Day from a specific date.

##### Endpoint

`GET /@today/qotd`

##### Options

| Option | Type | Description |
| --- | --- | --- |
| `date` | Query parameter | **Required**, the date in ISO format for which you would like to see the Quote of the Day. |

##### Responses

| Response | Description |
| --- | --- |
| `400` | "You must specify the date in query." The `date` field is missing from query parameters. |
| `400` | "Invalid date selection." You either picked a day for which there was no Quote of the Day, or a day in the future, or a day which has not yet finished (today). |
| `200` | "Success." See example below. |

##### Example responses

```json
{
  "message": "Success.",
  "data": {
    "quote": {
      "id": 2,
      "body": "Boba fett AYAYA Clap",
      "published": "2021-05-12 02:24:55.637066+00:00"
    },
    "author": {
      "user_id": "auth0|60933a869201390068ec9895",
      "nickname": "matootie",
      "picture": "https://cdn.auth0.com/avatars/ma.png"
    }
  }
}
```


#### Get Quotes to vote on

[Go back to header](#today-functionality)

Get two fresh quotes to submit a vote on or to create Meanings for.

##### Endpoint

`GET /@today/quotes`

##### Options

There are no options for this endpoint.

##### Responses

| Response | Description |
| --- | --- |
| `204` | There was either an unlucky draw or the user has seen all the quotes they can see without getting back duplicates. In this case, a background task is initiated to fetch the user fresh quotes as soon as they're available. |
| `200` | "Success." See example below. |

##### Example responses

```json
{
  "message": "Success.",
  "data": [
    {
      "id": 173,
      "body": "This is a Quote.",
      "published": "2021-05-05 22:05:03.029577+00:00"
    },
    {
      "id": 245,
      "body": "This is also a Quote.",
      "published": "2021-05-05 22:06:29.029577+00:00"
    },
  ]
}
```


#### Vote on a Quote

[Go back to header](#today-functionality)

Vote on a Quote that appears on your voting ballot.

##### Endpoint

`POST /@today/vote`

##### Options

| Option | Type | Description |
| --- | --- | --- |
| `vote` | Body field | **Required**, the ID of the Quote that you want to vote for. Must be on your voting ballot. Could be `0` if the user would like to skip the vote. |

##### Responses

| Response | Description |
| --- | --- |
| `400` | "Missing request body." You failed to include request body JSON. |
| `400` | "Missing vote field in request body." You need to provide a value for vote in request body. |
| `400` | "Missing Quotes to vote from." You need to query the ["get Quotes to vote on"](#get-quotes-to-vote-on) endpoint first to create a voting ballot. |
| `400` | "Invalid vote." The provided value for vote is not one of the IDs on the voting ballot or `0`. |
| `200` | "Success." See example below. |

##### Example responses

```json
{
  "message": "Success."
}
```


#### Submit a Quote for Quote of the Day

[Go back to header](#today-functionality)

Submit one of your quotes to be Quote of the Day.

##### Endpoint

`POST /@today/submit`

##### Options

| Option | Type | Description |
| --- | --- | --- |
| `quote_id` | Body field | **Required**, the Quote ID that you would like to submit. You must be the author of the Quote and it must have been written on the same day as you're submitting it. |

##### Responses

| Response | Description |
| --- | --- |
| `400` | "You already submitted a Quote for today." You are only allowed to submit one Quote per day. |
| `400` | "Missing request body." You failed to include request body JSON. |
| `400` | "Missing quote_id field in request body." You need to provide a value for quote_id in request body. |
| `400` | "You cannot submit a Quote that you didn't write." You must be the author of the Quote for which you are trying to submit. |
| `400` | "You can only submit Quotes that were written today." The Quote that you are trying to submit must have been written on the same day as the submission. |
| `200` | "Success." See example below. |

##### Example responses

```json
{
  "message": "Success."
}
```
