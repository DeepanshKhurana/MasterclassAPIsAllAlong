from pydantic import BaseModel, ConfigDict, Field


class TeamStats(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    team: str = Field(description="Team name")
    format: str = Field(description="Match format: Test, ODI, or T20")
    players: int | None = Field(default=None, description="Players in the squad snapshot")
    matches_played: int | None = Field(default=None, description="Total matches played")
    total_runs: int | None = Field(default=None, description="Total squad runs scored")
    average_batting_average: float | None = Field(
        default=None,
        description="Squad-wide average runs scored per dismissal. Higher is better.",
    )
    average_strike_rate: float | None = Field(
        default=None,
        description="Squad-wide average runs scored per 100 balls faced.",
    )


class LeaderboardEntry(BaseModel):
    rank: int = Field(description="Position on the leaderboard, 1 is best")
    name: str = Field(description="Team name")
    value: float = Field(description="Value of the ranking metric for this team")
    metric: str = Field(description="Name of the metric used to rank this entry")


