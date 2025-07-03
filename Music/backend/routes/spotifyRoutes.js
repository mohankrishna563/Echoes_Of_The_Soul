// backend/routes/spotifyRoutes.js
const express = require('express');
const router = express.Router();
const { searchTracks } = require('../spotify.js');

router.get('/search', async (req, res) => {
  const query = req.query.q;
  if (!query) {
    return res.status(400).json({ error: 'Missing search query' });
  }

  try {
    const results = await searchTracks(query);
    res.json(results);
  } catch (err) {
    console.error('Spotify search failed:', err.message);
    res.status(500).json({ error: 'Spotify search failed' });
  }
});

module.exports = router;
