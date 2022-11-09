# anicomp

To use, call the constructor for the Comparer class with a list of staff names to compare. Note that if you try to put in too many names at once, you will hit the rate limit for the AniList API, especially if you have people with long careers.

c = Comparer(["Miyazaki", "Takahata", "Kotabe])

The comparison table is stored as a pandas DataFrame in c.table

Names can be added with comp_multi. The table will update automatically to include the new staff members in the comparison. In this way, you can add as many people to the comparison as you want without breaking the rate limit.

c.comp_multi(["Kondo"])

TODO

Handle error when no staff returned by search

Better visualization of comparison table
