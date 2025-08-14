# AggieSpots

**AggieSpots**is a web app that helps Texas A&M students quickly find open classrooms to study in. When the usual spots like libraries are crowded, it shows real-time availability of classrooms across campus, giving students more choices for quiet, productive study spaces.

## Features

- Shows available classrooms across the Texas A&M campus.

- Ranks classrooms by distance from the user’s current location.

- Delivers real-time updates on classroom availability.

- Features an interactive map to view classroom locations.

- Offers a list view with live status for each classroom.

## Tech Stack

### Frontend

-   **Next.js**: Handles server-side rendering and provides a robust React-based framework for building the frontend UI.
-   **Mapbox GL**: Provides the interactive map to display classroom locations on Texas A&M campus.
-   **Tailwind CSS**: Used for styling the UI components with utility-first CSS for responsive and consistent design.
-   **Geolocation API**: Retrieves the user’s current location to sort classrooms by proximity.

### Backend

-   **Flask**: A lightweight Python web framework to handle API requests and logic for retrieving and processing classroom availability data.
-   **Requests**: A Python library used in Flask to fetch classroom data from external APIs.
-   **Haversine Formula**: Implemented in the backend to calculate the distance between the user and classroom locations based on coordinates.

#### DemoImage
![TAMU Spots](https://github.com/sirisha49/AggieSpot/blob/main/Aggiespots-main/DemoImage.png)


