"""Example how the functions in generate_schedule can be used.

This could be wrapped in a CLI, but that interface requires some thoughts to be
able to handle multiple events with different starting participants. This works
fine enough.
"""
import pathlib

from generate_schedule import (Participant, assign_weeks, generate_csv,
                               generate_ics)

###
# Define participants
part = [
    Participant(name)
    for name in (
        "Adam Adamsson",
        "Berit Beritsdotter",
        "Cecilia Ceciliadotter",
        "David Davidsson",
    )
]

###
# Assign weeks / events
part_with_e1 = assign_weeks(part, 2021, "Indoor cleaning week", "Adam Adamsson")
part_with_e2 = assign_weeks(
    part_with_e1, 2021, "Outdoor cleaning week", "Berit Beritsdotter"
)


###
# Generate ics files and save them
generate_ics(part_with_e2, pathlib.Path("generated/"))

###
# Generate csv files and save them
generate_csv(part_with_e2, pathlib.Path("generated/"))
