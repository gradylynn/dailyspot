# [The Daily Spot](https://gradylynn.com/dailyspot)
This is a simple daily game that I programmed mostly as a way for me to learn some React.

Some notes:
- I use [Create React App](https://github.com/facebook/create-react-app) to manage all things react.
(`npm start` for development, `npm run build` for production building)
- I use github action workflows to automate data updates. Every day, the track playcounts are updated.
Every three months, the schedule for future tracks is updates.
- I'm using [this repo](https://github.com/entriphy/sp-playcount) to get spotify playcount data
(which the creator is hosting [here](https://api.t4ils.dev/)). If that fails or goes down, that would be a big problem lol.
- interesting [reading](https://github.com/entriphy/sp-playcount-librespot/issues/28) about how he uses spotify's graphql api to get the data.
