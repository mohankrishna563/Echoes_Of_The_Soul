// backend/spotify.js
require('dotenv').config();
const SpotifyWebApi = require('spotify-web-api-node');

const spotifyApi = new SpotifyWebApi({
  clientId: process.env.SPOTIFY_CLIENT_ID,
  clientSecret: process.env.SPOTIFY_CLIENT_SECRET
});

async function getAccessToken() {
  const data = await spotifyApi.clientCredentialsGrant();
  spotifyApi.setAccessToken(data.body.access_token);
}

async function searchTracks(query) {
  await getAccessToken();
  const res = await spotifyApi.searchTracks(query, { limit: 10 });
  return res.body.tracks.items.map(track => ({
    name: track.name,
    artist: track.artists.map(a => a.name).join(', '),
    image: track.album.images[0]?.url || '',
    preview: track.preview_url
  }));
}

module.exports = { searchTracks };
