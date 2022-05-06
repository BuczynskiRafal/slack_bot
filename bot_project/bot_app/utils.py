import datetime
import calendar
from django.db.models import Sum
from .models import VotingResults
from .scrap_users import get_user, get_users

CATEGORIES = ["Team up to win", "Act to deliver", "Disrupt to grow"]


def total_points(ts_start=0, ts_end=9999999999.9) -> dict:
    """Calculate sum of points for each user for current month.
    @param ts_start: float - timestamp
    @param ts_end: float - timestamp
    @rtype: dict
    @return : dict contain sum of point for all slack users.
    """
    users = get_users()
    users_points = {}
    for user in users:
        users_points[user.slack_id] = calculate_points(user.slack_id, ts_start=ts_start, ts_end=ts_end)
    return users_points


def winner(ts_start=0.1, ts_end=9999999999.9) -> str:
    """Find the winners in each category for current month.
    @rtype: str
    @return: message contain information about winners
    """

    """Collect data form database."""
    users_points = total_points(ts_start=ts_start, ts_end=ts_end)
    winner_team_up_to_win = max(
        users_points, key=lambda v: users_points[v]["points_team_up_to_win"]
    )
    points_team_up_to_win = users_points[winner_team_up_to_win]["points_team_up_to_win"]
    winner_act_to_deliver = max(
        users_points, key=lambda v: users_points[v]["points_act_to_deliver"]
    )
    points_act_to_deliver = users_points[winner_act_to_deliver]["points_act_to_deliver"]
    winner_disrupt_to_grow = max(
        users_points, key=lambda v: users_points[v]["points_disrupt_to_grow"]
    )
    points_disrupt_to_grow = users_points[winner_disrupt_to_grow][
        "points_disrupt_to_grow"
    ]

    winners = [
        (winner_team_up_to_win, points_team_up_to_win),
        (winner_act_to_deliver, points_act_to_deliver),
        (winner_disrupt_to_grow, points_disrupt_to_grow),
    ]

    """Create message."""
    text = f"Wyniki głosowania w programie wyróżnień.\n"
    for i in range(3):
        text += f"W kategorii '{CATEGORIES[i]}' wygrywa '{get_user(winners[i][0]).name}', " \
                f"liczba głosów {winners[i][1]}.\n"
    return text


def get_start_end_day():
    """Calculate timestamp for start and end current day.
    @return:
        ts_start : timestamp of beginning current day.
        ts_end : timestamp of end current day.
    """
    today = datetime.datetime.now()
    start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end = today.replace(hour=23, minute=59, second=59, microsecond=9999)
    ts_start = datetime.datetime.timestamp(start)
    ts_end = datetime.datetime.timestamp(end)
    return ts_start, ts_end


def get_start_end_month():
    """Calculate timestamp for start and end current month.
    @return:
        ts_start : timestamp of beginning current day.
        ts_end : timestamp of end current day.
    """
    today = datetime.datetime.now()
    start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end = today.replace(day=calendar.monthrange(today.year, today.month)[1], hour=23, minute=59, second=59, microsecond=9999)
    ts_start = datetime.datetime.timestamp(start)
    ts_end = datetime.datetime.timestamp(end)
    return ts_start, ts_end


def validate_user_selection(voting_results: dict) -> bool:
    """Check if user not vote for the same user in many categories.
    @rtype: bool
    """
    team_up = voting_results[0]["selected_user"]
    act_to = voting_results[1]["selected_user"]
    disrupt = voting_results[2]["selected_user"]
    selections = [team_up, act_to, disrupt]
    if selections.count(None) >= 2:
        return True
    else:
        if team_up == act_to or team_up == disrupt or act_to == disrupt:
            return False
    return True


def validate_votes_himself(voting_results: dict, voting_user_id: str) -> bool:
    """Check if the user voted for himself.
    @rtype: bool
    """
    for i in range(3):
        if voting_results[i]["selected_user"]:
            if voting_results[i]["selected_user"] == voting_user_id:
                return False
        else:
            continue
    return True


def validate_points_amount(voting_results: dict) -> bool:
    """Check if sum all points is between 0-3.
    @rtype: bool
    """
    points = 0
    for i in range(3):
        if "points" in voting_results[i]:
            points += voting_results[i]["points"]
        else:
            points += 0
    return 0 <= points <= 3


def validate(voting_results: dict, voting_user_id: str) -> bool:
    """Check if data from request is validate.
    @return: bool : is validate data
    """
    return all(
        [
            validate_points_amount(voting_results),
            validate_votes_himself(voting_results, voting_user_id),
            validate_user_selection(voting_results),
        ]
    )


def error_message(voting_results: dict, voting_user_id: str) -> str:
    """Create errors message. Contain all errors.
    @rtype: str : error message
    """
    text = ""
    if not (
        validate_votes_himself(
            voting_results=voting_results, voting_user_id=voting_user_id
        )
    ):
        text += "You cannot vote for yourself.\n"
    if validate_user_selection(voting_results=voting_results) is False:
        text += "You cannot vote for the same user in two categories.\n"
    if validate_points_amount(voting_results=voting_results) is False:
        text += "You can give away a maximum of 3 points in all categories.\n"
    text += "Results were not saved."
    return text


def save_votes(voting_results: dict, voting_user: str) -> None:
    """Save votes to db.
    Create object and save in db,
    after then update object with data form slack voting form.
    @return: None
    """
    current_month = get_start_end_month()
    desc = VotingResults.objects.filter(voting_user_id=voting_user, ts__range=(current_month[0], current_month[1])).exists()
    """If voting user not in db, create object."""
    if not desc:
        print('not desc')
        voting_res = VotingResults.objects.create(
            voting_user_id=voting_user,
            ts=datetime.datetime.now().timestamp(),
        )
        voting_res.save()

    """If user in db, update object.
    The reason for this is that saving all data form form, 
    even if the form not complete."""
    if desc:
        voting_res = VotingResults.objects.get(voting_user_id=voting_user, ts__range=(current_month[0], current_month[1]))
        print(voting_res.id)
        try:
            voting_res.team_up_to_win = get_user(slack_id=voting_results[0]["selected_user"])
            voting_res.points_team_up_to_win = int(voting_results[0]["points"])
        except Exception as e:
            print('Missing data in Team up to win row')
        try:
            voting_res.act_to_deliver = get_user(
                slack_id=voting_results[1]["selected_user"]
            )
            voting_res.points_act_to_deliver = int(voting_results[1]["points"])
        except Exception as e:
            print('Missing data in Act to deliver row')
        try:
            voting_res.disrupt_to_grow = get_user(
                slack_id=voting_results[2]["selected_user"]
            )
            voting_res.points_disrupt_to_grow = int(voting_results[2]["points"])
        except Exception as e:
            print('Missing data in Disrupt to grow row')

        voting_res.ts = datetime.datetime.now().timestamp()
        voting_res.save(
            update_fields=[
                "team_up_to_win",
                "act_to_deliver",
                "disrupt_to_grow",
                "points_team_up_to_win",
                "points_act_to_deliver",
                "points_disrupt_to_grow",
                "ts",
            ]
        )


def prepare_data(request):
    """Decode data from request.
    @return: dict
    """
    decode_data = request.body.decode("utf-8")

    data = {}
    params = [param for param in decode_data.split("&")]
    for attributes in params:
        item = attributes.split("=")
        data[item[0]] = item[1]
    return data


def create_text(voting_user_id: str) -> str:
    """Create a message containing information on how the user voted.
    @return: str : information on how the user voted
    """
    current_month = get_start_end_month()
    voting_results = VotingResults.objects.get(
        voting_user_id=get_user(slack_id=voting_user_id),
        ts__range=(current_month[0], current_month[1])
    )
    text = f"Cześć {get_user(voting_user_id).name.split('.')[0].capitalize()}.\n"
    attributes = [
        (
            voting_results.team_up_to_win,
            voting_results.points_team_up_to_win,
            "Team up to win",
        ),
        (
            voting_results.act_to_deliver,
            voting_results.points_act_to_deliver,
            "Act to deliver",
        ),
        (
            voting_results.disrupt_to_grow,
            voting_results.points_disrupt_to_grow,
            "Disrupt to grow",
        ),
    ]
    for user, points, category in attributes:
        if user:
            text += f"W kategorii '{category}' wybrano użytkownika: '{user.name}', punkty: '{points}'.\n"
        else:
            text += f"W kategorii '{category}' nie dokonano wyboru.\n"
    return text


def calculate_points(voting_user_id, ts_start=0.1, ts_end=9999999999.9):
    points = {
        "points_team_up_to_win": VotingResults.objects.filter(
            team_up_to_win=get_user(voting_user_id), ts__range=(ts_start, ts_end)
        ).aggregate(Sum("points_team_up_to_win"))["points_team_up_to_win__sum"],
        "points_act_to_deliver": VotingResults.objects.filter(
            act_to_deliver=get_user(voting_user_id), ts__range=(ts_start, ts_end)
        ).aggregate(Sum("points_act_to_deliver"))["points_act_to_deliver__sum"],
        "points_disrupt_to_grow": VotingResults.objects.filter(
            disrupt_to_grow=get_user(voting_user_id), ts__range=(ts_start, ts_end)
        ).aggregate(Sum("points_disrupt_to_grow"))["points_disrupt_to_grow__sum"],
    }
    for k, v in points.items():
        if v is None:
            points[k] = 0
    return points
