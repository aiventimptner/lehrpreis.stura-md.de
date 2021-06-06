Hello {{ nomination.get_username|title }},

thank you for your nomination. As a last step, please confirm via this 
email that the nomination has been submitted by you. All you have to 
do is click on the link below. The link is valid until **{{ link.expiry }}**!

[confirm nomination]({{ link.url }})

For matching purposes, you can find your submitted details again below.

> {{ lecturer.get_full_name }} ({{ lecturer.faculty }})
>
> {{ nomination.reason }}

Best regards,  
your student council

--  
Student Council of the Otto-von-Guericke-University Magdeburg  
Building 26, Room 002  
Universitätsplatz 2  
39106 Magdeburg

Phone: 0391/67-58971  
Email: stura@ovgu.de  
Twitter: [@sturaOVGU](https://twitter.com/sturaOVGU)  
Instagram: [@stura_ovgu](https://www.instagram.com/stura_ovgu/)