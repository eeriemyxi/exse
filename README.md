# TODO
## Implement Caching for the Playlists
- See if user is connected to internet.
  - If connected, load the first 50 results, then incrementally load more when
    required. I think having multiple "batches" will be useful. Each batch will
    contain however many items that were fetched from an API call. The user then
    if they so wish, can reload a fine number or all batches through a
    interface. But I am not sure if batching is a good idea (think about the
    indexes).
    
    Whenever a batch is created, use `pickle` to backup the class (not batch) to
    disk.
    
  - If disconnected, load the last available backup of the class. If none is
    available, tell them to go online.
