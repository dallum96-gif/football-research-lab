from __future__ import annotations

import csv
import html
import json
import re
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "reference" / "club_profiles_v1.json"
IDENTITY = ROOT / "identity" / "team_seasons.csv"
IMAGE_DIR = ROOT / "web" / "public" / "club-profile"
REPORT = ROOT / "data" / "reference" / "club_profile_rollout_report_v1.json"

TODAY = "2026-09-10"

IMAGE_DIR.mkdir(parents=True, exist_ok=True)

USER_AGENT = (
    "Football Research Laboratory/1.0 "
    "(private football research project; contact via repository)"
)


def seed(
    *,
    full_name: str,
    wiki: str,
    nickname: str,
    founded: int | None,
    origin: str,
    home: str,
    locality: str,
    colours: list[tuple[str, str]],
    stadium: str,
    since: int | None,
    previous: str | None,
    story: str,
    milestones: list[tuple[int, str]],
    honours_slug: str,
) -> dict:
    return {
        "full_name": full_name,
        "wiki": wiki,
        "nickname": nickname,
        "founded": founded,
        "origin": origin,
        "home": home,
        "locality": locality,
        "colours": colours,
        "stadium": stadium,
        "since": since,
        "previous": previous,
        "story": story,
        "milestones": milestones,
        "honours_slug": honours_slug,
    }


SEEDS: dict[str, dict] = {
    "Arsenal": seed(
        full_name="Arsenal Football Club",
        wiki="Arsenal F.C.",
        nickname="The Gunners",
        founded=1886,
        origin="Woolwich, south-east London",
        home="North London",
        locality="Islington",
        colours=[("Red", "#d71920"), ("White", "#f5f1e8")],
        stadium="Emirates Stadium",
        since=2006,
        previous="Highbury · 1913–2006",
        story=(
            "Born among munitions workers in Woolwich in 1886, Arsenal crossed "
            "London in 1913 to make Highbury home. The club remained there for "
            "93 years before moving a short distance to Emirates Stadium in 2006."
        ),
        milestones=[(1886, "Woolwich"), (1913, "Highbury"), (2006, "Emirates")],
        honours_slug="arsenal",
    ),

    "Aston Villa": seed(
        full_name="Aston Villa Football Club",
        wiki="Aston Villa F.C.",
        nickname="The Villans",
        founded=1874,
        origin="Birmingham",
        home="Birmingham",
        locality="Aston",
        colours=[("Claret", "#670e36"), ("Blue", "#95bfe5")],
        stadium="Villa Park",
        since=1897,
        previous=None,
        story=(
            "Founded in Birmingham in 1874 by members of Villa Cross Wesleyan "
            "Chapel. A founder member of the Football League in 1888, Aston Villa "
            "have played at Villa Park since 1897."
        ),
        milestones=[(1874, "Founded"), (1888, "Football League"), (1897, "Villa Park")],
        honours_slug="aston-villa",
    ),

    "Bournemouth": seed(
        full_name="AFC Bournemouth",
        wiki="A.F.C. Bournemouth",
        nickname="The Cherries",
        founded=1899,
        origin="Boscombe",
        home="Bournemouth",
        locality="Dorset",
        colours=[("Red", "#d71920"), ("Black", "#111111")],
        stadium="Vitality Stadium",
        since=1910,
        previous=None,
        story=(
            "Founded in 1899 as Boscombe, the club grew from south-coast "
            "non-league football through the Football League and reached the "
            "Premier League for the first time in 2015. Dean Court has been "
            "its home since 1910."
        ),
        milestones=[(1899, "Boscombe"), (1910, "Dean Court"), (2015, "Premier League")],
        honours_slug="bournemouth",
    ),

    "Brentford": seed(
        full_name="Brentford Football Club",
        wiki="Brentford F.C.",
        nickname="The Bees",
        founded=1889,
        origin="Brentford",
        home="West London",
        locality="Brentford",
        colours=[("Red", "#e30613"), ("White", "#ffffff")],
        stadium="Gtech Community Stadium",
        since=2020,
        previous="Griffin Park · 1904–2020",
        story=(
            "Founded in 1889 after members of Brentford Rowing Club voted to "
            "establish a football team. Griffin Park was home from 1904 until "
            "the club moved to Brentford Community Stadium in 2020."
        ),
        milestones=[(1889, "Founded"), (1904, "Griffin Park"), (2020, "New home")],
        honours_slug="brentford",
    ),

    "Brighton and Hove Albion": seed(
        full_name="Brighton & Hove Albion Football Club",
        wiki="Brighton & Hove Albion F.C.",
        nickname="The Seagulls",
        founded=1901,
        origin="Brighton & Hove",
        home="Brighton & Hove",
        locality="Sussex",
        colours=[("Blue", "#0057b8"), ("White", "#ffffff")],
        stadium="American Express Stadium",
        since=2011,
        previous="Goldstone Ground · 1902–1997",
        story=(
            "Founded in 1901, Brighton played at the Goldstone Ground for most "
            "of the twentieth century. After years without a permanent home, "
            "the club moved into Falmer Stadium in 2011."
        ),
        milestones=[(1901, "Founded"), (1902, "Goldstone"), (2011, "Falmer")],
        honours_slug="brighton-and-hove-albion",
    ),

    "Burnley": seed(
        full_name="Burnley Football Club",
        wiki="Burnley F.C.",
        nickname="The Clarets",
        founded=1882,
        origin="Burnley",
        home="Burnley",
        locality="Lancashire",
        colours=[("Claret", "#6c1d45"), ("Blue", "#8fd2ee")],
        stadium="Turf Moor",
        since=1883,
        previous=None,
        story=(
            "Founded in 1882, Burnley were a founder member of the Football "
            "League in 1888. Turf Moor has been home since 1883, one of English "
            "football's longest continuous stadium associations."
        ),
        milestones=[(1882, "Founded"), (1883, "Turf Moor"), (1888, "Football League")],
        honours_slug="burnley",
    ),

    "Chelsea": seed(
        full_name="Chelsea Football Club",
        wiki="Chelsea F.C.",
        nickname="The Blues",
        founded=1905,
        origin="West London",
        home="West London",
        locality="Fulham",
        colours=[("Blue", "#034694"), ("White", "#ffffff")],
        stadium="Stamford Bridge",
        since=1905,
        previous=None,
        story=(
            "Founded in 1905 to play at Stamford Bridge, a ground that already "
            "existed before the club itself. Chelsea have remained there "
            "throughout their history."
        ),
        milestones=[(1905, "Founded"), (1905, "Stamford Bridge")],
        honours_slug="chelsea",
    ),

    "Coventry City": seed(
        full_name="Coventry City Football Club",
        wiki="Coventry City F.C.",
        nickname="The Sky Blues",
        founded=1883,
        origin="Coventry",
        home="Coventry",
        locality="West Midlands",
        colours=[("Sky blue", "#77bde9"), ("White", "#ffffff")],
        stadium="Coventry Building Society Arena",
        since=2005,
        previous="Highfield Road · 1899–2005",
        story=(
            "Founded in 1883 as Singers FC by workers at the Singer bicycle "
            "factory. Renamed Coventry City in 1898, the club left Highfield "
            "Road for the current arena in 2005."
        ),
        milestones=[(1883, "Singers FC"), (1898, "Coventry City"), (2005, "New ground")],
        honours_slug="coventry-city",
    ),

    "Crystal Palace": seed(
        full_name="Crystal Palace Football Club",
        wiki="Crystal Palace F.C.",
        nickname="The Eagles",
        founded=1861,
        origin="Crystal Palace",
        home="South London",
        locality="Selhurst",
        colours=[("Red", "#c4122e"), ("Blue", "#1b458f")],
        stadium="Selhurst Park",
        since=1924,
        previous=None,
        story=(
            "The professional club entered the Southern League in 1905 and "
            "initially played inside the Crystal Palace exhibition grounds. "
            "Selhurst Park has been home since 1924."
        ),
        milestones=[(1905, "Southern League"), (1924, "Selhurst Park")],
        honours_slug="crystal-palace",
    ),

    "Everton": seed(
        full_name="Everton Football Club",
        wiki="Everton F.C.",
        nickname="The Toffees",
        founded=1878,
        origin="Liverpool",
        home="Liverpool",
        locality="Bramley-Moore Dock",
        colours=[("Royal blue", "#003399"), ("White", "#ffffff")],
        stadium="Hill Dickinson Stadium",
        since=2025,
        previous="Goodison Park · 1892–2025",
        story=(
            "Founded in 1878 as St Domingo's and renamed Everton the following "
            "year. A founder member of the Football League, the club spent "
            "133 years at Goodison Park before moving to its new waterfront "
            "stadium in 2025."
        ),
        milestones=[(1878, "St Domingo's"), (1892, "Goodison"), (2025, "Waterfront")],
        honours_slug="everton",
    ),

    "Fulham": seed(
        full_name="Fulham Football Club",
        wiki="Fulham F.C.",
        nickname="The Cottagers",
        founded=1879,
        origin="West London",
        home="West London",
        locality="Fulham",
        colours=[("White", "#ffffff"), ("Black", "#111111")],
        stadium="Craven Cottage",
        since=1896,
        previous=None,
        story=(
            "Founded in 1879 as a church team in west London. Craven Cottage "
            "has been the club's home since 1896."
        ),
        milestones=[(1879, "Founded"), (1896, "Craven Cottage")],
        honours_slug="fulham",
    ),

    "Hull City": seed(
        full_name="Hull City Association Football Club",
        wiki="Hull City A.F.C.",
        nickname="The Tigers",
        founded=1904,
        origin="Kingston upon Hull",
        home="Kingston upon Hull",
        locality="East Yorkshire",
        colours=[("Amber", "#f5a12d"), ("Black", "#111111")],
        stadium="MKM Stadium",
        since=2002,
        previous="Boothferry Park · 1946–2002",
        story=(
            "Founded in 1904, Hull City entered the Football League a year later. "
            "Boothferry Park was home for more than half a century before the "
            "club moved to the current stadium in 2002."
        ),
        milestones=[(1904, "Founded"), (1946, "Boothferry Park"), (2002, "New home")],
        honours_slug="hull-city",
    ),

    "Ipswich Town": seed(
        full_name="Ipswich Town Football Club",
        wiki="Ipswich Town F.C.",
        nickname="The Tractor Boys",
        founded=1878,
        origin="Ipswich",
        home="Ipswich",
        locality="Suffolk",
        colours=[("Blue", "#0044aa"), ("White", "#ffffff")],
        stadium="Portman Road",
        since=1884,
        previous=None,
        story=(
            "Founded in 1878 and elected to the Football League in 1938. "
            "Portman Road has been home since 1884; Ipswich won the English "
            "title in their first top-flight season in 1961/62."
        ),
        milestones=[(1878, "Founded"), (1884, "Portman Road"), (1962, "Champions")],
        honours_slug="ipswich-town",
    ),

    "Leeds United": seed(
        full_name="Leeds United Football Club",
        wiki="Leeds United F.C.",
        nickname="The Whites",
        founded=1919,
        origin="Leeds",
        home="Leeds",
        locality="West Yorkshire",
        colours=[("White", "#ffffff"), ("Blue", "#1d428a")],
        stadium="Elland Road",
        since=1919,
        previous=None,
        story=(
            "Founded in 1919 after the dissolution of Leeds City. Elland Road, "
            "already established as the city's football ground, has been Leeds "
            "United's home throughout the club's history."
        ),
        milestones=[(1919, "Founded"), (1919, "Elland Road")],
        honours_slug="leeds-united",
    ),

    "Leicester City": seed(
        full_name="Leicester City Football Club",
        wiki="Leicester City F.C.",
        nickname="The Foxes",
        founded=1884,
        origin="Leicester",
        home="Leicester",
        locality="East Midlands",
        colours=[("Blue", "#003090"), ("White", "#ffffff")],
        stadium="King Power Stadium",
        since=2002,
        previous="Filbert Street · 1891–2002",
        story=(
            "Founded in 1884 as Leicester Fosse and renamed Leicester City in "
            "1919. Filbert Street was home for 111 years before the club moved "
            "to its current stadium in 2002."
        ),
        milestones=[(1884, "Leicester Fosse"), (1919, "Leicester City"), (2002, "New home")],
        honours_slug="leicester-city",
    ),

    "Liverpool": seed(
        full_name="Liverpool Football Club",
        wiki="Liverpool F.C.",
        nickname="The Reds",
        founded=1892,
        origin="Liverpool",
        home="Liverpool",
        locality="Anfield",
        colours=[("Red", "#c8102e"), ("White", "#ffffff")],
        stadium="Anfield",
        since=1892,
        previous=None,
        story=(
            "Founded in 1892 after a split between Everton and Anfield owner "
            "John Houlding. The new club took Anfield as its home and has "
            "played there ever since."
        ),
        milestones=[(1892, "Founded"), (1892, "Anfield")],
        honours_slug="liverpool",
    ),

    "Manchester City": seed(
        full_name="Manchester City Football Club",
        wiki="Manchester City F.C.",
        nickname="The Citizens",
        founded=1880,
        origin="West Gorton",
        home="Manchester",
        locality="East Manchester",
        colours=[("Sky blue", "#6cabdd"), ("White", "#ffffff")],
        stadium="Etihad Stadium",
        since=2003,
        previous="Maine Road · 1923–2003",
        story=(
            "Formed in 1880 as St Mark's (West Gorton), later Ardwick, and "
            "renamed Manchester City in 1894. The club left Maine Road in 2003 "
            "for the City of Manchester Stadium, now the Etihad."
        ),
        milestones=[(1880, "St Mark's"), (1894, "Manchester City"), (2003, "Etihad")],
        honours_slug="manchester-city",
    ),

    "Manchester United": seed(
        full_name="Manchester United Football Club",
        wiki="Manchester United F.C.",
        nickname="The Red Devils",
        founded=1878,
        origin="Newton Heath",
        home="Greater Manchester",
        locality="Old Trafford",
        colours=[("Red", "#da291c"), ("White", "#ffffff")],
        stadium="Old Trafford",
        since=1910,
        previous=None,
        story=(
            "Founded in 1878 as Newton Heath LYR by railway workers and renamed "
            "Manchester United in 1902. Old Trafford has been the club's home "
            "since 1910."
        ),
        milestones=[(1878, "Newton Heath"), (1902, "Manchester United"), (1910, "Old Trafford")],
        honours_slug="manchester-united",
    ),

    "Middlesbrough": seed(
        full_name="Middlesbrough Football Club",
        wiki="Middlesbrough F.C.",
        nickname="Boro",
        founded=1876,
        origin="Middlesbrough",
        home="Middlesbrough",
        locality="Teesside",
        colours=[("Red", "#e11b22"), ("White", "#ffffff")],
        stadium="Riverside Stadium",
        since=1995,
        previous="Ayresome Park · 1903–1995",
        story=(
            "Founded in 1876 by members of Middlesbrough Cricket Club. "
            "Ayresome Park was home from 1903 until the club moved to the "
            "Riverside Stadium in 1995."
        ),
        milestones=[(1876, "Founded"), (1903, "Ayresome Park"), (1995, "Riverside")],
        honours_slug="middlesbrough",
    ),

    "Newcastle United": seed(
        full_name="Newcastle United Football Club",
        wiki="Newcastle United F.C.",
        nickname="The Magpies",
        founded=1892,
        origin="Newcastle upon Tyne",
        home="Newcastle upon Tyne",
        locality="Tyneside",
        colours=[("White", "#ffffff"), ("Black", "#111111")],
        stadium="St James' Park",
        since=1892,
        previous=None,
        story=(
            "Newcastle United emerged in 1892 as Newcastle East End took over "
            "the lease at St James' Park and adopted the United name. "
            "St James' Park has remained the club's home."
        ),
        milestones=[(1892, "Newcastle United"), (1892, "St James' Park")],
        honours_slug="newcastle-united",
    ),

    "Norwich City": seed(
        full_name="Norwich City Football Club",
        wiki="Norwich City F.C.",
        nickname="The Canaries",
        founded=1902,
        origin="Norwich",
        home="Norwich",
        locality="Norfolk",
        colours=[("Yellow", "#fff200"), ("Green", "#00a650")],
        stadium="Carrow Road",
        since=1935,
        previous="The Nest · 1908–1935",
        story=(
            "Founded in 1902 and nicknamed the Canaries. After early years at "
            "Newmarket Road and the Nest, Norwich moved to Carrow Road in 1935."
        ),
        milestones=[(1902, "Founded"), (1908, "The Nest"), (1935, "Carrow Road")],
        honours_slug="norwich-city",
    ),

    "Nottingham Forest": seed(
        full_name="Nottingham Forest Football Club",
        wiki="Nottingham Forest F.C.",
        nickname="Forest",
        founded=1865,
        origin="Nottingham",
        home="Nottingham",
        locality="Trent",
        colours=[("Red", "#dd0000"), ("White", "#ffffff")],
        stadium="City Ground",
        since=1898,
        previous=None,
        story=(
            "Founded in 1865, Nottingham Forest were among the early clubs to "
            "shape organised football in England. The City Ground has been "
            "their home since 1898."
        ),
        milestones=[(1865, "Founded"), (1898, "City Ground"), (1979, "European champions")],
        honours_slug="nottingham-forest",
    ),

    "Sheffield United": seed(
        full_name="Sheffield United Football Club",
        wiki="Sheffield United F.C.",
        nickname="The Blades",
        founded=1889,
        origin="Sheffield",
        home="Sheffield",
        locality="South Yorkshire",
        colours=[("Red", "#ee2737"), ("White", "#ffffff")],
        stadium="Bramall Lane",
        since=1889,
        previous=None,
        story=(
            "Founded in 1889 by the Sheffield United Cricket Club. Bramall Lane, "
            "one of the world's oldest major sporting grounds, has been the "
            "club's home since formation."
        ),
        milestones=[(1889, "Founded"), (1889, "Bramall Lane")],
        honours_slug="sheffield-united",
    ),

    "Southampton": seed(
        full_name="Southampton Football Club",
        wiki="Southampton F.C.",
        nickname="The Saints",
        founded=1885,
        origin="Southampton",
        home="Southampton",
        locality="Hampshire",
        colours=[("Red", "#d71920"), ("White", "#ffffff")],
        stadium="St Mary's Stadium",
        since=2001,
        previous="The Dell · 1898–2001",
        story=(
            "Founded in 1885 by members of St Mary's Church, the origin of the "
            "Saints nickname. The Dell was home for 103 years before the move "
            "to St Mary's Stadium in 2001."
        ),
        milestones=[(1885, "St Mary's"), (1898, "The Dell"), (2001, "St Mary's Stadium")],
        honours_slug="southampton",
    ),

    "Stoke City": seed(
        full_name="Stoke City Football Club",
        wiki="Stoke City F.C.",
        nickname="The Potters",
        founded=1863,
        origin="Stoke-on-Trent",
        home="Stoke-on-Trent",
        locality="Staffordshire",
        colours=[("Red", "#e03a3e"), ("White", "#ffffff")],
        stadium="bet365 Stadium",
        since=1997,
        previous="Victoria Ground · 1878–1997",
        story=(
            "Founded in the nineteenth century and among the Football League's "
            "founder members in 1888. The Victoria Ground was home for 119 years "
            "before the move to the Britannia Stadium in 1997."
        ),
        milestones=[(1863, "Origins"), (1888, "Football League"), (1997, "New home")],
        honours_slug="stoke-city",
    ),

    "Sunderland": seed(
        full_name="Sunderland Association Football Club",
        wiki="Sunderland A.F.C.",
        nickname="The Black Cats",
        founded=1879,
        origin="Sunderland",
        home="Sunderland",
        locality="Wearside",
        colours=[("Red", "#eb172b"), ("White", "#ffffff")],
        stadium="Stadium of Light",
        since=1997,
        previous="Roker Park · 1898–1997",
        story=(
            "Founded in 1879 by schoolteacher James Allan as Sunderland and "
            "District Teachers AFC. Roker Park was home for almost a century "
            "before the club moved to the Stadium of Light in 1997."
        ),
        milestones=[(1879, "Founded"), (1898, "Roker Park"), (1997, "Stadium of Light")],
        honours_slug="sunderland",
    ),

    "Swansea City": seed(
        full_name="Swansea City Association Football Club",
        wiki="Swansea City A.F.C.",
        nickname="The Swans",
        founded=1912,
        origin="Swansea",
        home="Swansea",
        locality="South Wales",
        colours=[("White", "#ffffff"), ("Black", "#111111")],
        stadium="Swansea.com Stadium",
        since=2005,
        previous="Vetch Field · 1912–2005",
        story=(
            "Founded in 1912 as Swansea Town and admitted to the Football League "
            "in 1920. The Vetch Field was home until 2005, when the club moved "
            "to its current stadium."
        ),
        milestones=[(1912, "Swansea Town"), (1920, "Football League"), (2005, "New home")],
        honours_slug="swansea-city",
    ),

    "Tottenham Hotspur": seed(
        full_name="Tottenham Hotspur Football Club",
        wiki="Tottenham Hotspur F.C.",
        nickname="Spurs",
        founded=1882,
        origin="Tottenham",
        home="North London",
        locality="Tottenham",
        colours=[("White", "#ffffff"), ("Navy", "#132257")],
        stadium="Tottenham Hotspur Stadium",
        since=2019,
        previous="White Hart Lane · 1899–2017",
        story=(
            "Founded in 1882 by members of the Hotspur Cricket Club. White Hart "
            "Lane became home in 1899; Tottenham moved into the new Tottenham "
            "Hotspur Stadium on the same site in 2019."
        ),
        milestones=[(1882, "Founded"), (1899, "White Hart Lane"), (2019, "New stadium")],
        honours_slug="tottenham-hotspur",
    ),

    "Watford": seed(
        full_name="Watford Football Club",
        wiki="Watford F.C.",
        nickname="The Hornets",
        founded=1881,
        origin="Watford",
        home="Watford",
        locality="Hertfordshire",
        colours=[("Yellow", "#fbee23"), ("Black", "#111111")],
        stadium="Vicarage Road",
        since=1922,
        previous=None,
        story=(
            "The club's roots trace to Watford Rovers in 1881, with the modern "
            "club formed through merger in 1898. Vicarage Road has been home "
            "since 1922."
        ),
        milestones=[(1881, "Watford Rovers"), (1898, "Watford FC"), (1922, "Vicarage Road")],
        honours_slug="watford",
    ),

    "West Bromwich Albion": seed(
        full_name="West Bromwich Albion Football Club",
        wiki="West Bromwich Albion F.C.",
        nickname="The Baggies",
        founded=1878,
        origin="West Bromwich",
        home="West Bromwich",
        locality="West Midlands",
        colours=[("White", "#ffffff"), ("Navy", "#122f67")],
        stadium="The Hawthorns",
        since=1900,
        previous=None,
        story=(
            "Founded in 1878 as West Bromwich Strollers by workers at George "
            "Salter's Spring Works. The Hawthorns has been the club's home "
            "since 1900."
        ),
        milestones=[(1878, "Strollers"), (1888, "Football League"), (1900, "The Hawthorns")],
        honours_slug="west-bromwich-albion",
    ),

    "West Ham United": seed(
        full_name="West Ham United Football Club",
        wiki="West Ham United F.C.",
        nickname="The Hammers",
        founded=1895,
        origin="Thames Ironworks",
        home="East London",
        locality="Stratford",
        colours=[("Claret", "#7a263a"), ("Blue", "#1bb1e7")],
        stadium="London Stadium",
        since=2016,
        previous="Boleyn Ground · 1904–2016",
        story=(
            "Founded in 1895 as Thames Ironworks by workers from the Thames "
            "Ironworks and Shipbuilding Company. Renamed West Ham United in "
            "1900, the club moved from the Boleyn Ground to London Stadium in 2016."
        ),
        milestones=[(1895, "Thames Ironworks"), (1900, "West Ham"), (2016, "London Stadium")],
        honours_slug="west-ham-united",
    ),

    "Wolverhampton Wanderers": seed(
        full_name="Wolverhampton Wanderers Football Club",
        wiki="Wolverhampton Wanderers F.C.",
        nickname="Wolves",
        founded=1877,
        origin="Wolverhampton",
        home="Wolverhampton",
        locality="West Midlands",
        colours=[("Old gold", "#fdb913"), ("Black", "#111111")],
        stadium="Molineux",
        since=1889,
        previous=None,
        story=(
            "Founded in 1877 as St Luke's and known as Wolverhampton Wanderers "
            "from 1879. Molineux has been the club's home since 1889."
        ),
        milestones=[(1877, "St Luke's"), (1879, "Wanderers"), (1889, "Molineux")],
        honours_slug="wolverhampton-wanderers",
    ),

    "Huddersfield Town": seed(
        full_name="Huddersfield Town Association Football Club",
        wiki="Huddersfield Town A.F.C.",
        nickname="The Terriers",
        founded=1908,
        origin="Huddersfield",
        home="Huddersfield",
        locality="West Yorkshire",
        colours=[("Blue", "#0e63ad"), ("White", "#ffffff")],
        stadium="John Smith's Stadium",
        since=1994,
        previous="Leeds Road · 1908–1994",
        story=(
            "Founded in 1908, Huddersfield became the first English club to win "
            "three consecutive league titles in the 1920s. Leeds Road was home "
            "until the move to the current stadium in 1994."
        ),
        milestones=[(1908, "Founded"), (1926, "Three in a row"), (1994, "New home")],
        honours_slug="huddersfield-town",
    ),

    "Cardiff City": seed(
        full_name="Cardiff City Football Club",
        wiki="Cardiff City F.C.",
        nickname="The Bluebirds",
        founded=1899,
        origin="Cardiff",
        home="Cardiff",
        locality="South Wales",
        colours=[("Blue", "#0070b5"), ("White", "#ffffff")],
        stadium="Cardiff City Stadium",
        since=2009,
        previous="Ninian Park · 1910–2009",
        story=(
            "Founded in 1899 as Riverside AFC and renamed Cardiff City in 1908. "
            "Ninian Park was home for almost a century before the club moved to "
            "Cardiff City Stadium in 2009."
        ),
        milestones=[(1899, "Riverside"), (1908, "Cardiff City"), (2009, "New home")],
        honours_slug="cardiff-city",
    ),

    "Luton Town": seed(
        full_name="Luton Town Football Club",
        wiki="Luton Town F.C.",
        nickname="The Hatters",
        founded=1885,
        origin="Luton",
        home="Luton",
        locality="Bedfordshire",
        colours=[("Orange", "#f78f1e"), ("White", "#ffffff")],
        stadium="Kenilworth Road",
        since=1905,
        previous=None,
        story=(
            "Founded in 1885 from a merger of local clubs. Kenilworth Road "
            "has been Luton Town's home since 1905."
        ),
        milestones=[(1885, "Founded"), (1905, "Kenilworth Road")],
        honours_slug="luton-town",
    ),
}


CURRENT_2026_27 = {
    "Arsenal",
    "Aston Villa",
    "Bournemouth",
    "Brentford",
    "Brighton and Hove Albion",
    "Chelsea",
    "Coventry City",
    "Crystal Palace",
    "Everton",
    "Fulham",
    "Hull City",
    "Ipswich Town",
    "Leeds United",
    "Liverpool",
    "Manchester City",
    "Manchester United",
    "Newcastle United",
    "Nottingham Forest",
    "Sunderland",
    "Tottenham Hotspur",
}


def request_bytes(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT},
    )

    with urllib.request.urlopen(
        request,
        timeout=25,
    ) as response:
        return response.read()


def request_json(url: str) -> dict:
    return json.loads(
        request_bytes(url).decode("utf-8")
    )


def normalise_name(value: str) -> str:
    return value.replace("_", " ").strip()


def slugify(value: str) -> str:
    return re.sub(
        r"[^a-z0-9]+",
        "-",
        value.casefold(),
    ).strip("-")


def strip_tags(value: str) -> str:
    return html.unescape(
        re.sub(r"<[^>]+>", "", value or "")
    ).strip()


def wikipedia_wikitext(title: str) -> str | None:
    params = urllib.parse.urlencode(
        {
            "action": "query",
            "prop": "revisions",
            "rvprop": "content",
            "rvslots": "main",
            "titles": title,
            "format": "json",
            "formatversion": "2",
        }
    )

    try:
        payload = request_json(
            f"https://en.wikipedia.org/w/api.php?{params}"
        )

        pages = payload.get("query", {}).get(
            "pages",
            [],
        )

        if not pages:
            return None

        return (
            pages[0]
            .get("revisions", [{}])[0]
            .get("slots", {})
            .get("main", {})
            .get("content")
        )
    except Exception:
        return None


def wiki_field(
    wikitext: str | None,
    field: str,
) -> str | None:
    if not wikitext:
        return None

    match = re.search(
        rf"^\|\s*{re.escape(field)}\s*=\s*(.+?)\s*$",
        wikitext,
        flags=re.I | re.M,
    )

    return match.group(1).strip() if match else None


def clean_wiki(value: str | None) -> str | None:
    if not value:
        return None

    value = re.sub(
        r"<ref[^>]*>.*?</ref>",
        "",
        value,
        flags=re.I | re.S,
    )

    value = re.sub(
        r"<ref[^>]*/>",
        "",
        value,
        flags=re.I,
    )

    value = re.sub(
        r"\[\[([^\]|]+)\|[^\]]+\]\]",
        r"\1",
        value,
    )

    value = re.sub(
        r"\[\[([^\]]+)\]\]",
        r"\1",
        value,
    )

    for _ in range(4):
        updated = re.sub(
            r"\{\{(?:nowrap|small|plainlist)\|([^{}]+)\}\}",
            r"\1",
            value,
            flags=re.I,
        )

        if updated == value:
            break

        value = updated

    value = re.sub(r"\{\{[^{}]*\}\}", "", value)
    value = value.replace("'''", "").replace("''", "")
    value = strip_tags(value)
    value = re.sub(r"\s+", " ", value).strip(" ,;")

    return value or None


def capacity_from_wiki(wikitext: str | None) -> int | None:
    raw = wiki_field(wikitext, "capacity")

    if not raw:
        return None

    for match in re.findall(
        r"\d[\d,\s]{3,}",
        raw,
    ):
        digits = re.sub(r"\D", "", match)

        if digits:
            value = int(digits)

            if 5000 <= value <= 150000:
                return value

    return None


class TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.table_depth = 0
        self.in_row = False
        self.in_cell = False
        self.cell_parts: list[str] = []
        self.row: list[str] = []
        self.rows: list[list[str]] = []

    def handle_starttag(
        self,
        tag: str,
        attrs,
    ) -> None:
        if tag == "table":
            self.table_depth += 1

        if self.table_depth and tag == "tr":
            self.in_row = True
            self.row = []

        if (
            self.in_row
            and tag in {"td", "th"}
        ):
            self.in_cell = True
            self.cell_parts = []

    def handle_data(self, data: str) -> None:
        if self.in_cell:
            self.cell_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if (
            self.in_cell
            and tag in {"td", "th"}
        ):
            text = re.sub(
                r"\s+",
                " ",
                " ".join(self.cell_parts),
            ).strip()

            self.row.append(text)
            self.in_cell = False

        if self.in_row and tag == "tr":
            if len(self.row) >= 2:
                self.rows.append(self.row)

            self.in_row = False

        if tag == "table" and self.table_depth:
            self.table_depth -= 1


def honour_bucket(name: str) -> tuple[str, str] | None:
    value = name.casefold().strip()

    if (
        "premier league" in value
        or "league division one" in value
        or value == "first division"
    ):
        return "league", "League titles"

    if "fa cup" in value and "youth" not in value:
        return "fa_cup", "FA Cup"

    if (
        "league cup" in value
        or "efl cup" in value
    ):
        return "league_cup", "League Cup"

    if (
        "charity shield" in value
        or "community shield" in value
    ):
        return "community_shield", "Community Shield"

    european_tokens = (
        "european cup",
        "champions league",
        "uefa cup",
        "europa league",
        "conference league",
        "cup winners",
        "fairs cup",
        "inter-cities fairs",
        "intertoto",
        "super cup",
    )

    if any(token in value for token in european_tokens):
        return "europe", "Europe"

    if (
        "second division" in value
        or "division two" in value
        or "championship" in value
    ):
        return "second_tier", "Second tier"

    if (
        "third division" in value
        or "division three" in value
        or "league one" in value
    ):
        return "third_tier", "Third tier"

    if (
        "fourth division" in value
        or "division four" in value
        or "league two" in value
    ):
        return "fourth_tier", "Fourth tier"

    if (
        "football league trophy" in value
        or "efl trophy" in value
    ):
        return "efl_trophy", "EFL Trophy"

    return None


HONOUR_PRIORITY = {
    "league": 1,
    "fa_cup": 2,
    "league_cup": 3,
    "europe": 4,
    "community_shield": 5,
    "second_tier": 6,
    "third_tier": 7,
    "fourth_tier": 8,
    "efl_trophy": 9,
}


def fetch_honours(slug: str) -> tuple[list[dict], bool]:
    url = (
        f"https://www.11v11.com/teams/"
        f"{slug}/tab/honours/"
    )

    try:
        source = request_bytes(url).decode(
            "utf-8",
            errors="ignore",
        )
    except Exception:
        return [], False

    parser = TableParser()
    parser.feed(source)

    counts: dict[str, dict] = {}

    for row in parser.rows:
        if len(row) < 2:
            continue

        competition = row[0].strip()
        placing = row[1].casefold()

        winner = (
            "winner" in placing
            or "champion" in placing
        ) and "runner" not in placing

        if not winner:
            continue

        bucket = honour_bucket(competition)

        if not bucket:
            continue

        key, label = bucket

        item = counts.setdefault(
            key,
            {
                "key": key,
                "label": label,
                "wins": 0,
            },
        )

        item["wins"] += 1

    values = list(counts.values())

    values.sort(
        key=lambda item: HONOUR_PRIORITY.get(
            item["key"],
            99,
        )
    )

    return values[:5], True


def commons_image(
    stadium: str,
    locality: str,
) -> dict | None:
    search = (
        f'{stadium} {locality} football stadium exterior'
    )

    params = urllib.parse.urlencode(
        {
            "action": "query",
            "generator": "search",
            "gsrsearch": search,
            "gsrnamespace": "6",
            "gsrlimit": "12",
            "prop": "imageinfo",
            "iiprop": "url|mime|extmetadata",
            "iiurlwidth": "1600",
            "format": "json",
            "formatversion": "2",
        }
    )

    try:
        payload = request_json(
            f"https://commons.wikimedia.org/w/api.php?{params}"
        )
    except Exception:
        return None

    for page in payload.get(
        "query",
        {},
    ).get("pages", []):
        infos = page.get("imageinfo") or []

        if not infos:
            continue

        info = infos[0]

        mime = str(info.get("mime") or "")

        if mime not in {
            "image/jpeg",
            "image/png",
        }:
            continue

        metadata = info.get("extmetadata") or {}

        licence = (
            metadata.get(
                "LicenseShortName",
                {},
            ).get("value")
            or ""
        )

        licence_lower = licence.casefold()

        if not (
            licence_lower.startswith("cc ")
            or "public domain" in licence_lower
        ):
            continue

        image_url = (
            info.get("thumburl")
            or info.get("url")
        )

        if not image_url:
            continue

        return {
            "url": image_url,
            "source": info.get("descriptionurl"),
            "mime": mime,
            "credit": strip_tags(
                metadata.get(
                    "Artist",
                    {},
                ).get("value", "")
            ),
            "licence": licence,
            "licence_url": (
                metadata.get(
                    "LicenseUrl",
                    {},
                ).get("value")
                or None
            ),
        }

    return None


def add_source(
    profile: dict,
    source: dict,
) -> None:
    sources = profile.setdefault(
        "sources",
        [],
    )

    if not any(
        item.get("id") == source["id"]
        for item in sources
    ):
        sources.append(source)


with IDENTITY.open(
    "r",
    encoding="utf-8-sig",
    newline="",
) as handle:
    identity_rows = list(
        csv.DictReader(handle)
    )

with REGISTRY.open(
    "r",
    encoding="utf-8",
) as handle:
    document = json.load(handle)

profiles = document.get("profiles") or []

by_name = {
    normalise_name(
        str(profile.get("canonical_name") or "")
    ): profile
    for profile in profiles
}

image_success = 0
honours_success = 0
leadership_success = 0
profile_success = 0
missing_seeds: list[str] = []
image_failures: list[str] = []
honours_failures: list[str] = []

for canonical_name, profile in sorted(
    by_name.items()
):
    info = SEEDS.get(canonical_name)

    if info is None:
        missing_seeds.append(canonical_name)
        continue

    # Arsenal already has the reviewed seed from the proof-of-concept.
    preserve_curated = (
        canonical_name == "Arsenal"
        and profile.get("status") == "CURATED"
    )

    wiki_text = wikipedia_wikitext(
        info["wiki"]
    )

    capacity = capacity_from_wiki(
        wiki_text
    )

    manager = clean_wiki(
        wiki_field(
            wiki_text,
            "manager",
        )
    )

    captain = clean_wiki(
        wiki_field(
            wiki_text,
            "captain",
        )
    )

    if not preserve_curated:
        profile["status"] = "PARTIAL"
        profile["verified_as_of"] = TODAY

        profile["identity"] = {
            "full_name": info["full_name"],
            "nickname": info["nickname"],
            "founded_year": info["founded"],
            "origin": info["origin"],
            "home": info["home"],
            "locality": info["locality"],
            "colours": [
                {
                    "name": name,
                    "hex": colour,
                }
                for name, colour
                in info["colours"]
            ],
        }

        profile["story"] = {
            "text": info["story"],
            "milestones": [
                {
                    "year": year,
                    "label": label,
                }
                for year, label
                in info["milestones"]
            ],
        }

        profile["stadium"] = {
            "name": info["stadium"],
            "capacity": capacity,
            "since_year": info["since"],
            "previous_home": info["previous"],
        }

    add_source(
        profile,
        {
            "id": f"wikipedia-{slugify(canonical_name)}",
            "publisher": "Wikipedia",
            "url": (
                "https://en.wikipedia.org/wiki/"
                + urllib.parse.quote(
                    info["wiki"].replace(" ", "_")
                )
            ),
            "use": (
                "Provisional club-profile curation reference; "
                "official-source review remains required."
            ),
        },
    )

    # Current leadership belongs only to the living season.
    if (
        canonical_name in CURRENT_2026_27
        and (manager or captain)
    ):
        leadership = (
            profile.setdefault(
                "leadership_by_season",
                {},
            )
        )

        existing = leadership.get("2026-27")

        if not existing:
            leadership["2026-27"] = {
                "manager": (
                    {
                        "name": manager,
                        "detail": None,
                    }
                    if manager
                    else None
                ),
                "captain": (
                    {
                        "name": captain,
                        "detail": None,
                    }
                    if captain
                    else None
                ),
            }

        leadership_success += 1

    # Honours acquisition.
    existing_honours = (
        profile.get("honours") or {}
    )

    if not (
        preserve_curated
        and existing_honours.get("categories")
    ):
        honours, honours_ok = fetch_honours(
            info["honours_slug"]
        )

        profile["honours"] = {
            "as_of": TODAY if honours_ok else None,
            "source_status": (
                "OBSERVED"
                if honours_ok
                else "UNAVAILABLE"
            ),
            "note": (
                "Current all-time senior honours snapshot from "
                "a provisional reference source. Categories are "
                "mapped for compact Team Profile presentation and "
                "are not reconstructed as-of the selected season."
                if honours_ok
                else
                "Honours acquisition unavailable; no zero claim is made."
            ),
            "categories": honours,
        }

        if honours_ok:
            honours_success += 1

            add_source(
                profile,
                {
                    "id": f"11v11-{slugify(canonical_name)}-honours",
                    "publisher": "11v11",
                    "url": (
                        f"https://www.11v11.com/teams/"
                        f"{info['honours_slug']}/tab/honours/"
                    ),
                    "use": (
                        "Provisional all-time honours reference; "
                        "source-rights and official-source review required."
                    ),
                },
            )
        else:
            honours_failures.append(
                canonical_name
            )
    else:
        honours_success += 1

    # Licensed stadium photography.
    visual = profile.setdefault(
        "visual",
        {},
    )

    if visual.get("hero_image"):
        image_success += 1
    else:
        image = commons_image(
            info["stadium"],
            info["home"],
        )

        if image:
            ext = (
                ".jpg"
                if image["mime"] == "image/jpeg"
                else ".png"
            )

            filename = (
                f"{slugify(canonical_name)}"
                f"-stadium{ext}"
            )

            path = IMAGE_DIR / filename

            try:
                path.write_bytes(
                    request_bytes(image["url"])
                )

                visual.update(
                    {
                        "hero_image":
                            f"/club-profile/{filename}",
                        "hero_image_credit":
                            image["credit"] or "Wikimedia Commons contributor",
                        "hero_image_licence":
                            image["licence"],
                        "hero_image_licence_url":
                            image["licence_url"],
                        "hero_image_source":
                            image["source"],
                    }
                )

                image_success += 1
            except Exception:
                image_failures.append(
                    canonical_name
                )
        else:
            image_failures.append(
                canonical_name
            )

    profile_success += 1

    # Be respectful to external sources.
    time.sleep(0.15)


document["schema_version"] = "1.1.0"
document["profile_rollout"] = {
    "date": TODAY,
    "seeded_profiles": profile_success,
    "greyscale_visual_policy": True,
    "current_leadership_scope": "2026-27 only",
    "honours_temporal_scope": "current all-time snapshot",
}

REGISTRY.write_text(
    json.dumps(
        document,
        indent=2,
        ensure_ascii=False,
    )
    + "\n",
    encoding="utf-8",
)

report = {
    "date": TODAY,
    "persistent_clubs_in_registry": len(profiles),
    "biographical_profiles_seeded": profile_success,
    "stadium_images_available": image_success,
    "honours_sources_observed": honours_success,
    "current_2026_27_leadership_observed": leadership_success,
    "identity_clubs_without_seed": missing_seeds,
    "stadium_image_failures": image_failures,
    "honours_failures": honours_failures,
}

REPORT.write_text(
    json.dumps(
        report,
        indent=2,
        ensure_ascii=False,
    )
    + "\n",
    encoding="utf-8",
)

print()
print("FRL CLUB PROFILE ROLLOUT")
print("=" * 50)
print(
    f"Biography seeds:        {profile_success}"
)
print(
    f"Stadium images:         {image_success}"
)
print(
    f"Honours observed:       {honours_success}"
)
print(
    f"2026/27 leadership:     {leadership_success}"
)

if missing_seeds:
    print()
    print(
        "Persistent clubs still needing biography seed:"
    )

    for name in missing_seeds:
        print(f"  - {name}")

if image_failures:
    print()
    print("Image review required:")

    for name in image_failures:
        print(f"  - {name}")

if honours_failures:
    print()
    print("Honours review required:")

    for name in honours_failures:
        print(f"  - {name}")