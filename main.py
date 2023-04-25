import dotenv
import os
import patreon as pat_api
import discord as ds_api
import datetime
import random
import string
import asyncio

from patreon.jsonapi.parser import JSONAPIResource


# class DiscCode:
#     def __init__(self, member: Member, ):


class Member:
    def gen_disc_codes(self):
        self.disc_codes = {}
        coupon = []
        coupon_count = 1
        if self.tier == 'Groupie':
            coupon = ['10% Off In-Store Purchases']
        elif self.tier == 'Rock Star':
            coupon = ['15% Off In-Store Purchases']
        elif self.tier == 'Superhero':
            coupon = ['20% Off In-Store Purchases', 'Half-Off Admission to Live Shows']
            coupon_count = 2
        elif self.tier == 'Top Dog':
            coupon = ['30% Off In-Store Purchases', 'Free Admission to Live Shows']
            coupon_count = 2
        for i in range(coupon_count):
            letters = string.ascii_letters + string.digits
            code = ''.join(random.choice(letters) for i in range(10))
            self.disc_codes[coupon[i]] = code

    def __init__(self, data: list[JSONAPIResource] | JSONAPIResource):
        # if not debug:
        self.disc_codes = {}
        self.tier: str = data.relationship('reward').attribute('title')
        self.about: str = data.relationship('patron').attribute('about')
        self.created: datetime.datetime = data.relationship('patron').attribute('created')
        self.discord_id: int = data.relationship('patron').attribute('discord_id')
        self.email: str = data.relationship('patron').attribute('email')
        self.facebook: str = data.relationship('patron').attribute('facebook')
        self.facebook_id: int = data.relationship('patron').attribute('facebook_id')
        self.first_name: str = data.relationship('patron').attribute('first_name')
        self.full_name: str = data.relationship('patron').attribute('full_name')
        self.gender: int = data.relationship('patron').attribute('gender')
        self.has_password: bool = data.relationship('patron').attribute('has_password')
        self.image_url: str = data.relationship('patron').attribute('image_url')
        self.is_deleted: bool = data.relationship('patron').attribute('is_deleted')
        self.is_email_verified: bool = data.relationship('patron').attribute('is_email_verified')
        self.is_nuked: bool = data.relationship('patron').attribute('is_nuked')
        self.is_suspended: bool = data.relationship('patron').attribute('is_suspended')
        self.last_name: str = data.relationship('patron').attribute('last_name')
        self.social_connections: dict = data.relationship('patron').attribute('social_connections')
        self.thumb_url: str = data.relationship('patron').attribute('thumb_url')
        self.twitch: str = data.relationship('patron').attribute('twitch')
        self.twitter: str = data.relationship('patron').attribute('twitter')
        self.url: str = data.relationship('patron').attribute('url')
        self.vanity: str = data.relationship('patron').attribute('vanity')
        self.youtube: str = data.relationship('patron').attribute('youtube')
        # else:
        #     self.disc_codes = {}
        #     self.tier: str = 'Top Dog'
        #     self.about: str = 'I am James'
        #     self.created: datetime.datetime = None
        #     self.discord_id: int = 348935840501858306
        #     self.email: str = 'jamesedmiller8@gmail.com'
        #     self.facebook: str = ''
        #     self.facebook_id: int = 0
        #     self.first_name: str = 'James'
        #     self.full_name: str = 'James Miller'
        #     self.gender: int = 0
        #     self.has_password: bool = True
        #     self.image_url: str = ''
        #     self.is_deleted: bool = False
        #     self.is_email_verified: bool = False
        #     self.is_nuked: bool = False
        #     self.is_suspended: bool = False
        #     self.last_name: str = 'Miller'
        #     self.social_connections: dict = {}
        #     self.thumb_url: str = ''
        #     self.twitch: str = ''
        #     self.twitter: str = ''
        #     self.url: str = ''
        #     self.vanity: str = 'JMTNTBANG'
        #     self.youtube: str = 'https://youtube.com/@jmtntbang'


class Patreon:
    def refresh_pledges(self):
        print(f'({datetime.datetime.now()}) Refreshing Pledges...')
        # if debug:
        #     print(f'({datetime.datetime.now()}) Debug Override...')
        #     member = Member(data=None, debug=debug)
        #     self.pledges = {member.full_name: member}
        # else:
        pledges = self.client.fetch_page_of_pledges(self.campaign_id, 999999)
        for pledge in pledges.data():
            member = Member(pledge)
            self.pledges[member.full_name] = member
        # if debug2:
        #     member = Member(data=None, debug=True)
        #     self.pledges[member.full_name] = member
        print(f'({datetime.datetime.now()}) Refreshed Pledges')

    def __init__(self, token):
        print(f'({datetime.datetime.now()}) Connecting to Patreon...')
        self.client = pat_api.API(token)
        print(f'({datetime.datetime.now()}) Connected to Patreon')
        print(f'({datetime.datetime.now()}) Fetching Campaign...')
        self.campaign = self.client.fetch_campaign()
        self.campaign_id = self.campaign.data()[0].id()
        print(f'({datetime.datetime.now()}) Fetched Campaign')
        self.pledges = {}
        self.refresh_pledges()
        self.codes = []


dotenv.load_dotenv()
patreon: Patreon = Patreon(os.getenv('PATREON'))
discord_intents = ds_api.Intents.all()
discord = ds_api.Client(intents=discord_intents)


@discord.event
async def on_ready():
    # wait = datetime.datetime.today()
    # wait2 = wait.replace(hour=0, minute=34, second=0)
    while True:
    #     wait3 = wait2 - wait
    #     if wait3.days == -1:
    #         wait = datetime.datetime.today()
    #         wait2 = wait.replace(minute=wait2.minute+1)
    #         wait3 = wait2 - wait
    #     await asyncio.sleep(wait3.seconds)
        patreon.codes = []
        patreon.refresh_pledges()
        missing_discord = ds_api.Embed(
            title='Patrons Missing Linked Discord',
            description='These patrons do not have a Discord Linked, here are their Coupon Codes for Manual Forwarding'
        )
        for member in patreon.pledges:
            print(f'({datetime.datetime.now()}) Generating Coupons for Patron: {member}...')
            member = patreon.pledges[member]
            member.disc_codes = {}
            member.gen_disc_codes()
            if member.discord_id:
                member_discord = discord.get_user(member.discord_id)
                embed = ds_api.Embed(title='Today\'s Coupon Codes!',
                                     description='Here is a list of coupon codes that you get as a benefit from Patreon'
                                                 '!')
                for coupon in member.disc_codes:
                    embed.add_field(name=coupon, value=member.disc_codes[coupon])
                    patreon.codes.append({'name': coupon, 'code': member.disc_codes[coupon]})
                print(f'({datetime.datetime.now()}) Sending Coupons to {member.full_name}\'s Discord ({member_discord.display_name}#'
                      f'{member_discord.discriminator})...')
                member_dm = await discord.create_dm(member_discord)
                await member_dm.send(embed=embed)
            else:
                print(f'({datetime.datetime.now()}) Member {member.full_name} Does not have a Discord Linked, Code will be generated anyway and for'
                      f'warded to Server to be sent Manually')
                value = ''
                for coupon in member.disc_codes:
                    value += f'**{coupon}**: {member.disc_codes[coupon]}\n'
                    patreon.codes.append({'name': coupon, 'code': member.disc_codes[coupon]})
                missing_discord.add_field(
                    name=member.full_name,
                    value=value
                )
        await discord.get_guild(1053851544765874216).get_channel(1053858714911776790).send(embed=missing_discord)
        print(f'({datetime.datetime.now()}) Forwarding Coupons to Server...')
        embed = ds_api.Embed(
            title='Today\'s Coupon Codes!',
            description='These are the codes that can be used for today from Patrons'
        )
        ten_pc_off_codes = ''
        fifteen_pc_off_codes = ''
        twenty_pc_off_codes = ''
        thirty_pc_off_codes = ''
        half_off_admission_codes = ''
        free_admission_codes = ''
        for coupon in patreon.codes:
            if coupon['name'] == '10% Off In-Store Purchases':
                ten_pc_off_codes += f'{coupon["code"]}\n'
            if coupon['name'] == '15% Off In-Store Purchases':
                fifteen_pc_off_codes += f'{coupon["code"]}\n'
            if coupon['name'] == '20% Off In-Store Purchases':
                twenty_pc_off_codes += f'{coupon["code"]}\n'
            if coupon['name'] == '30% Off In-Store Purchases':
                thirty_pc_off_codes += f'{coupon["code"]}\n'
            if coupon['name'] == 'Half-Off Admission to Live Shows':
                half_off_admission_codes += f'{coupon["code"]}\n'
            if coupon['name'] == 'Free Admission to Live Shows':
                free_admission_codes += f'{coupon["code"]}\n'
        embed.add_field(
            name='10% Off In-Store Purchases',
            value=ten_pc_off_codes
        )
        embed.add_field(
            name='15% Off In-Store Purchases',
            value=fifteen_pc_off_codes
        )
        embed.add_field(
            name='20% Off In-Store Purchases',
            value=twenty_pc_off_codes
        )
        embed.add_field(
            name='30% Off In-Store Purchases',
            value=thirty_pc_off_codes
        )
        embed.add_field(
            name='Half-Off Admission to Live Shows',
            value=half_off_admission_codes
        )
        embed.add_field(
            name='Free Admission to Live Shows',
            value=free_admission_codes
        )
        await discord.get_guild(1053851544765874216).get_channel(1053858714911776790).send(embed=embed)
        print(f'({datetime.datetime.now()}) Done!')
        await asyncio.sleep(604800)

discord.run(os.getenv('DISCORD'))
