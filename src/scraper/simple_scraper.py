import json
import os
import time
from typing import List, Dict

def create_sample_data(output_dir: str) -> List[Dict]:
    """Create sample data about The Door church for testing purposes"""
    
    # Based on our earlier analysis of thedoor.org
    sample_pages = [
        {
            'url': 'https://thedoor.org/',
            'title': 'The Door - Together We Practice the Presence and Way of Jesus',
            'content': '''The Door is a church in Maple Grove, Minnesota where we practice the presence and way of Jesus together. 
            We gather every Sunday at 10am for worship, teaching, and community. Our services typically last 75-85 minutes.
            We're located at 9060 Zanzibar Lane North in Maple Grove.
            
            Our mission is to help people move from factories to fields, from performance to practice, 
            from fan to follower, from for God to with God, and from owner to steward.
            
            We believe spiritual growth is a process and we welcome vulnerability and imperfection. 
            We focus on active discipleship over passive membership.''',
            'scraped_at': time.time()
        },
        {
            'url': 'https://thedoor.org/about',
            'title': 'About The Door Church',
            'content': '''The Door is a compassionate community committed to spiritual formation and growth.
            We emphasize practicing the presence and way of Jesus in our daily lives.
            
            Our core values include:
            - Spiritual growth as a process
            - Welcoming vulnerability and imperfection  
            - Active discipleship over passive membership
            - Compassionate community
            - Local and global mission participation
            
            We offer various ministries including Kids ministry, Students ministry, and Young Adults programs.''',
            'scraped_at': time.time()
        },
        {
            'url': 'https://thedoor.org/sundays',
            'title': 'Sunday Services at The Door',
            'content': '''Join us every Sunday at 10am for worship at The Door.
            Location: 9060 Zanzibar Lane North, Maple Grove, MN
            Service Length: 75-85 minutes
            
            What to expect:
            - Welcoming community atmosphere
            - Contemporary worship music
            - Practical Bible teaching
            - Time for connection and fellowship
            - Childcare and kids programs available
            
            We dress casually and welcome people from all backgrounds and stages of faith.''',
            'scraped_at': time.time()
        },
        {
            'url': 'https://thedoor.org/get-involved',
            'title': 'Get Involved at The Door',
            'content': '''There are many ways to get involved at The Door:
            
            Newcomer's Gathering - A great first step to learn more about The Door
            Small Groups - Connect with others in smaller community settings
            Serve Teams - Use your gifts to serve others in our community
            Local Mission - Serve in our Maple Grove community
            Global Mission - Participate in international mission opportunities
            
            Ministry Areas:
            - Kids Ministry (birth through 5th grade)
            - Students Ministry (middle and high school)
            - Young Adults (college age and young professionals)
            - Worship Team
            - Welcome Team
            - Production Team''',
            'scraped_at': time.time()
        },
        {
            'url': 'https://thedoor.org/grow-in-faith',
            'title': 'Grow in Faith at The Door',
            'content': '''At The Door, we believe spiritual growth is a journey, not a destination.
            We offer various opportunities to grow in faith:
            
            Bible Study Groups - Dive deeper into Scripture with others
            Prayer Ministry - Learn to pray and be prayed for
            Spiritual Formation Classes - Explore spiritual disciplines
            Mentorship - Connect with mature believers for guidance
            Service Opportunities - Grow through serving others
            
            We emphasize moving:
            - From factories to fields (seeing life as more than productivity)
            - From performance to practice (grace over works)
            - From fan to follower (commitment over casual interest)
            - From for God to with God (partnership in the Kingdom)
            - From owner to steward (generous living)''',
            'scraped_at': time.time()
        },
        {
            'url': 'https://thedoor.org/leadership',
            'title': 'Leadership at The Door',
            'content': '''The Door is led by a team of pastors and leaders committed to shepherding our community.
            
            Our leadership team brings diverse backgrounds and experiences to serve our church family.
            They are committed to:
            - Teaching God's Word with clarity and relevance
            - Caring for the spiritual needs of our community
            - Casting vision for our mission and values
            - Developing other leaders
            - Modeling the way of Jesus in their own lives
            
            Leadership at The Door operates with transparency, accountability, and a heart for service.
            We believe in shared leadership and empowering others to use their gifts.''',
            'scraped_at': time.time()
        }
    ]
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Save as JSON
    with open(os.path.join(output_dir, 'scraped_pages.json'), 'w', encoding='utf-8') as f:
        json.dump(sample_pages, f, indent=2, ensure_ascii=False)
    
    # Save individual text files
    for i, page in enumerate(sample_pages):
        filename = f"page_{i:03d}_{page['url'].split('/')[-1] or 'home'}.txt"
        with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
            f.write(f"Title: {page['title']}\n")
            f.write(f"URL: {page['url']}\n")
            f.write(f"Content:\n{page['content']}")
    
    print(f"Created {len(sample_pages)} sample pages in {output_dir}")
    return sample_pages

if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from config.config import Config
    
    create_sample_data(Config.RAW_DATA_PATH)