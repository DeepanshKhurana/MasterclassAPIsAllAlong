from pydantic import BaseModel, ConfigDict, Field

class RecentInnings(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    match_id: str = Field(description="Cricsheet match identifier")
    date: str | None = Field(default=None, description="Match date, YYYY-MM-DD")
    venue: str | None = Field(default=None, description="Ground where this was played")
    batting_team: str | None = Field(default=None, description="Team that was batting")
    bowling_team: str | None = Field(default=None, description="Team that was bowling")
    score: float | None = Field(default=None, description="Runs scored in the innings")
    overs: float | None = Field(default=None, description="Overs faced in the innings")
    match_winner: str | None = Field(
        default=None, description="Team that won the match, if decided"
    )

class TeamForm(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    team: str = Field(description="Team name")
    match_type: str = Field(description="Match format, e.g. T20")
    games: int | None = Field(
        default=None, description="Matches computed from raw ball-by-ball data"
    )
    won: int | None = Field(default=None, description="Matches won")
    win_percentage: float | None = Field(default=None, description="Win rate, 0-100")
    runs: int | None = Field(default=None, description="Total runs scored across matches")
    recent_innings: list[RecentInnings] = Field(
        description="Most recent innings this team batted or bowled in"
    )

class BallEvent(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    innings: int = Field(description="Innings number, 1 for the first innings batted")
    over: int = Field(description="Over number, starting at 0")
    ball: int = Field(description="Ball number within the over, starting at 1")
    batter: str = Field(description="Batter facing the delivery")
    non_striker: str = Field(description="Batter at the non-striker's end")
    bowler: str = Field(description="Bowler delivering the ball")
    runs_batter: int = Field(description="Runs scored by the batter off the bat")
    runs_extras: int = Field(
        description="Extra runs conceded on the delivery, e.g. wides or no-balls"
    )
    runs_total: int = Field(description="Total runs scored on the delivery")
    wicket: bool = Field(description="Whether a wicket fell on this delivery")
    wicket_kind: str | None = Field(
        default=None, description="How the batter was dismissed, if a wicket fell"
    )
    player_dismissed: str | None = Field(
        default=None, description="Player dismissed on this delivery, if any"
    )
