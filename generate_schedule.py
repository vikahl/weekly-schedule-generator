"""Collection of functions and classes to generate recurring schedules.

The events in the schedule are weekly.
"""
import copy
import csv
import dataclasses
import datetime
import pathlib
from typing import List

import icalendar  # type: ignore


@dataclasses.dataclass
class Event:
    """An event, occurs during a time period and has a name.

    A supporting function can return the event as a icalendar-ready Event
    class.
    """

    name: str
    start: datetime.date
    end: datetime.date

    def get_as_ical(self) -> icalendar.Event:
        """Return the event as icalendar Event."""
        cal_ev = icalendar.Event()
        cal_ev.add("summary", self.name)
        cal_ev.add("dtstart", self.start)
        cal_ev.add("dtend", self.end)
        return cal_ev


@dataclasses.dataclass
class Participant:
    """Dataclass for participant.

    Has a name and can be assigned multiple events."""

    name: str
    events: List[Event] = dataclasses.field(default_factory=list)


def get_empty_calendar() -> icalendar.Calendar:
    """Returns an empty calendar with the necessary settings."""
    cal = icalendar.Calendar()
    # These are required to be a compliant ical file
    cal.add("prodid", "-//Weekly schedule generator/1.0/EN")
    cal.add("version", "2.0")
    return cal


def assign_weeks(
    participants: List[Participant], year: int, event: str, start_participant: str
) -> List[Participant]:
    """Assign weeks of year to participants, starting with start_participant

    If the number of participants are fewer than weeks in the current year, it
    will wrap around so that all weeks are assigned. The function returns a
    list of new Participants with weeks assigned.
    """

    assignees = [copy.deepcopy(p) for p in participants]
    num_assignees = len(assignees)
    try:
        start_idx = assignees.index(
            next((p for p in assignees if p.name == start_participant))
        )
    except StopIteration as ex:
        raise RuntimeError(
            "start_participant was not found in list of participants"
        ) from ex

    # Get the last week of the current year
    last_week = datetime.date(year, 12, 31).isocalendar()[1]

    for week in range(1, last_week + 1):
        # Get the assignee for the current week, modified so that the
        # start_participant gets the first week.
        assignees[((start_idx + week) % num_assignees - 1)].events.append(
            Event(
                name=event,
                start=datetime.datetime.strptime(f"{year}-{week}-1", "%G-%V-%u").date(),
                end=datetime.datetime.strptime(f"{year}-{week+1}-1", "%G-%V-%u").date(),
            )
        )

    return assignees


def generate_ics(participants: List[Participant], folder: pathlib.Path) -> None:
    """Generate ics files for the participants events.

    One file will be generated for each participant. The files will be saved to
    folder.
    """

    for participant in participants:
        cal = get_empty_calendar()

        for event in participant.events:
            cal.add_component(event.get_as_ical())

        with open(folder / f"{participant.name}.ics", "wb") as out_file:
            out_file.write(cal.to_ical())


def generate_csv(participants: List[Participant], folder: pathlib.Path) -> None:
    """Generates one csv file per event type with participants and schedules.

    The CSV files are structured as:
    participant name, week, start date, end date
    and are unordered
    """

    # Find all events types
    events: dict = {}
    for p in participants:
        for e in p.events:
            events.setdefault(e.name, [])
            events[e.name].append({"event": e, "participant": p})

    for event_name, values in events.items():
        with open(folder / f"{event_name}.csv", "w") as fh:
            writer = csv.writer(fh, delimiter=",")
            writer.writerow(["Participant", "Week", "Start date", "End date"])

            for value in values:
                e = value["event"]
                writer.writerow(
                    [
                        value["participant"].name,
                        e.start.strftime("%V"),
                        str(e.start),
                        str(e.end),
                    ]
                )
