# TODO
## Implement Caching for the Playlists
- See if user is connected to internet.
  - If the user is connected then fetching the first batch (offset 0) is a must.
    Do not do anything else. When the user needs to see the next batch, load it
    from cache if available, if not, then fetch it. Save it to cache after
    fetching it.
  
  - If the user is not connected, all the fetching is done from cache. Error
    should be raised if the request is not already cached.
