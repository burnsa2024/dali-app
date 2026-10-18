HELPFUL TOOLS PAGE:
    This page is split into a volunteer-focused section and a normal person-focused section. 
    Normal people
    - Register yourself: To ensure that all records are traceable and as accurate as possible, 
      only volunteers can register individuals when they show up at a shelter. However, this form 
      serves as a way that individuals can register themselves. This would be a different form that 
      doesn't require a login, but all entries would have to be approved by 
    - View a Shelter Map: This would allow people to visualize where they are (since evacuations are 
      so quick and chaotic that many people don't know where exactly they ended up), and would also 
      allow searchers to visualize where people have travelled, if they have moved between multiple 
      shelters. Shelters should have a collection of printed out maps as well for their residents to use
      so this map would serve as a up-to-date map that shelters can always print out. The location field
      in the shelter model currently does not a standardized form, so for this feature to be best implemented,
      that location field should be switched to an exact location, using GeoDjango or another geographcial
      library to allow users to input coordinates, addresses, or other exact coordinates that can be easily
      parsed by this map interface to display the exact location of each shelter.
    Volunteers
     - Edit/delete/check out residents. Although volunteers can easily access all records through
       the admin page, the only way to access that site is to type in the URL, since there are no links
       to the admin page directly on the site. Therefore, these options will provide volunteers with an easy
       way to make changes to any existing records in the database. 