# Philosopher

Philosopher is the back-end for the Kwot app. It handles creation of all Quotes and Meanings. Submissions for Quote of the Day, voting on Quote of the Day, as well as relationships between users (friendships).

## API

You must be authorized to access all endpoints. More information on authorization will be available soon.



### Quotes and Meanings

Users can write as many Quotes as they want. Each user on the platform is only allowed to submit one Meaning per Quote. A Quote is meant to be some sort of meaningful text, and a Meaning is meant to describe the readers interpretation of the Quote.


#### Get all Quotes

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


#### Get all Meanings for a Quote

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

Documentation for this service will be available soon.