import random

cyber_security_qoutes = [
    "The best defense is a good offense.",
    "There are only two types of organizations: Those that have been hacked and those that don't know it yet!",
    "Security isn't something you buy, it's something you do, and it takes talented people to do it right",
    "Security is a process, not a product.",
    "Security is a journey, not a destination.",
    "If it's smart, it's vulnerable",
    "Security should be built in, not bolt-on",
    "Security is a team sport",
    "If you can't afford security, you can't afford a breach",
    "Never underestimate a developer with a deadline",
    "Don't pet strange dogs. In other words, if it doesn't feel right, don't click on it",
    "If you're not paranoid, you're not paying attention",
    "Given the choice between dancing pigs and security, users will pick dancing pigs every time",
    "Give a man an 0day and he'll have access for a day, teach a man to phish and he'll have access for life",
    "The most secure computer is the computer that's off",
]


def generate_email_template(
    _hash,
    user_name,
    time,
    category_title,
    severity_color,
    severity,
    site_url,
    qoute=random.choice(cyber_security_qoutes),
) -> tuple:
    return (
        f"""
    {_hash}
    Dear {user_name},
    An activity with the hash {_hash} has been detected at {time}.
    In the category {category_title}.
    Please take action as soon as possible

    {severity}
    Take Action here: {site_url}

    {qoute}
    """,

    f"""

    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8" />
    </head>
    <body>
        <!-- Change text-color, background-color, font-size -->
        <table
        width="100%"
        border="0"
        cellpadding="0"
        cellspacing="0"
        style="color: #000000; background-color: #f6f6f9; font-size: 16px"
        >
        <!-- Change space above logo -->
        <tr height="40"></tr>
        <tr>
            <td></td>

            <!-- Width of email - default: 560px -->
            <td style="width: 560px">
            <!-- Logo -->
            <center>
                <img width="145" src="logo-image-url" />
            </center>

            <center>
                <h1>{_hash}</h1>
            </center>

            </td>

            <!-- Change space below logo -->
        </tr>

        <tr height="20"></tr>

        <!-- Start of content -->
        <tr>
            <td></td>
            <td style="background: #ffffff; padding: 26px 40px">
            Dear {user_name},<br /><br />
            An activity with the hash {_hash} has been detected at {time}. </br>
            In the category {category_title}.<br />
            Please take action as soon as possible <br />

            <p style="color:{severity_color};" >{severity}</p>
            <!-- Button -->
            <table cellspacing="0" cellpadding="0">
                <tr>
                <td style="border-radius: 4px" bgcolor="7380e">
                    <a
                    href="https://{site_url}"
                    target="_blank"
                    style="
                        padding: 12px 16px;
                        border-radius: 4px;
                        color: #ffffff;
                        text-decoration: none;
                        display: inline-block;
                    "
                    >
                    Take Action</a
                    >
                </td>
                </tr>
            </table>
            </td>
        </tr>

        <!-- Footer -->
        <tr height="80" style="font-size: 12px">
            <td></td>
            <td>
            <center>
                {qoute}
            </center>
            </td>
            <td></td>
        </tr>
        </table>
    </body>
    </html>
    """,
    )
