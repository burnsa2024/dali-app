Live deployed link: https://dali-application-burns.onrender.com
    Note: this link is deployed using a free version of Render, meaning that the site may take up to a minute
          to start up. Please be patient, and a Render loading screen is normal!

HOW TO USE:
     - A username and password is needed to access the registration page of the site. I have created
       a sample volunteer profile for the purpose of reviewing this site:
         Username: admin-test
         Password: DALI_APPLICATION
       Once logged in, you can view the admin page of this site at https://dali-application-burns.onrender.com/admin. 
       This displays everything in the database (registered people, searches, matches, shelters, etc). 
        
Overview: This site implements a system to easily register people who have been displaced from their homes,
          while also allowing anyone to search for people in the database. Registration is mainly through 
          shelters (volunteers have their own login associated with a certain shelter for simple record-tracking),
          although individuals can register themselves through a different form if they have access to the Internet 
          and are not at a shelter. 

Notes on search and register design decisions: 
    All searches are manually reviewed - the database is initially searched for matches
    in name, but all searches are reviewed to ensure that false matches are minimized. There may be many people
    with the same name, from similar areas, and who are even searching for similarly named people, so the best way to
    ensure that we don't have false search results is to have volunteers speak with the people who appeared in the search
    result to see if they are the correct person, and to see if they actually want to be found. Although this approach
    puts far more labor on the volunteers, it is essential for the safety and privacy of people.
    Similarly, currently only volunteers are able to register people. This ensures that all registrations can be tracked 
    to a specific shelter where a volunteer saw a person. This means that false information is easier to track and remove. 
    I envision an implementation of a system where anyone in the public can fill out a form to register themselves as safe,
    but this form should have additional review to prevent people from knowingly adding false information to the system, or
    searching for people with malicious intent. 

Example: There is currently one registered person in the database (name: Alex Burns, age: 20, ...). You can view this entry
         by going to the admin page of the site and clicking on "Person records". Play with the search functionality by searching
         for exact name matches, similar name matches, simlar age, etc, and then check the "Matches" database section of the admin
         page to see the results of each search. You can also register a new person of your choosing (once logged in, see above) and
         explore the search functionality for your new registered person.

Screenshots: 
![Search page](search.png) - The results of the search page. Gives the searcher the necessary information to follow up with the search in the future (reference code)
![img.png](registration_submission.png) - Screen shown upon submitting the registration. Note that the site redirects the user back to the site, since the
                  volunteer is likely registering multiple people at once, so this redirect system saves the volunteer valuable time.

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

Design decisions: the website is as simple as possible, with the two primary buttons clearly visible at the top of the 
    navigation bar. This is to make it as easy as possible for volunteers to use. There is only one other page (tools)
    that can be accessed from the homepage - this is a dump of other helpful but less important parts of the site that volunteers and
    the public will use less frequently. 

Future Work on this Site:
    1. Allow volunteers to upload the provided Excel sheet so that many people can be registered at once. 
       An electronic copy could be uploaded and parsed, creating a database object for each person. The next step
       (far more difficult) would be to allow volunteers to upload a picture of a printed and hand-filled-out version
       of this table, which save volunteers lots of time, especially when access to Internet and cellular service is limited.
    2. Add automated email or SMS communication. Once a user submits a search, they should recieve a confirmation email, and if
       there are plausible matches, the volunteers at the shelter with the match should get notified. SMS is likely more resilient
       against outages caused by the natural disaster, but is harder to implement. 
    3. Improve the ease of updating records. Add a page dedicated to volunteers updating records to show that people moved to a different
       shelter, that they were found by someone who was searching for them. This makes volunteer responsibilities easier, while making the app
       more functional at helping people find each other. 

AI Use:
    Much of the code on this project was initially written by AI (primarily Claude chatbot, not Claude Code), 
    and then modified to fit the structure, content, approach, and desire that I wanted. The creativity and design
    of this project are primarily human generated by me, and AI was used as a tool to quickly implement a basic 
    prototype that is somewhat functional. My approach to AI is that it is an amazing tool to get a minimum viable product
    as quickly as possible. Then, extensive testing, modification, and code review can be done to fine-tune the application
    to the exact purposes and to make sure that the AI-generated code is satisfactory. Sufficient testing and review of an application
    (such as writing tests, making alterations to the code, finding bugs, following the workflow, etc.) will result in humans reading
    through and understanding all of the code (in a true comprehensive review, which any application should have before deployment), so
    using AI to create an MVP is a huge time-saver, and bugs/mistakes will inevitably be caught by humans through add-ons and testing.
    Therefore, my ideal workflow (which is also how I tackled this application problem) is to have humans come up with ideas and a thourough
    plan of what the application should look like, then have AI implement a MVP, and then add on to this MVP, test it, review it, etc, and
    through working with the code, it will become clear whether the AI-generated code is safe, functional, and usable, and much of this code
    ultimately does get replaced by human code as the project grows, but AI-heavy approaches to an MVP are acceptable in my mind since it saves
    unfathomable amounts of time. All of this 