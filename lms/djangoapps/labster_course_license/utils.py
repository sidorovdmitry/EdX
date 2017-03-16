"""
Utils for Labster LTI Passport.
"""
import re
import logging
from urlparse import urlparse

from django.core.validators import URLValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from xmodule.modulestore.django import modulestore

from opaque_keys.edx.keys import CourseKey, UsageKey


log = logging.getLogger(__name__)
WILD_CARD = '*'


class SimulationValidationError(Exception):
    """
    This exception is raised when the simulation has invalid values.
    """
    pass


class LtiPassportError(Exception):
    """
    This exception is raised in the case where Lti Passport is incorrect.
    """
    pass


class LtiPassport(object):
    """
    Works with lti passports.
    """
    slots = ['lti_id', 'consumer_key', 'secret_key']

    def __init__(self, passport_str):
        self.lti_id, self.consumer_key, self.secret_key = self.parse(passport_str)

    @classmethod
    def parse(cls, passport_str):
        """
        Parses a `passport_str (str)` and retuns lti_id, consumer key, secret key.
        """
        try:
            return tuple(i.strip() for i in passport_str.split(':'))
        except ValueError:
            msg = _('Could not parse LTI passport: {lti_passport}. Should be "id:key:secret" string.').format(
                lti_passport='{0!r}'.format(passport_str)
            )
            raise LtiPassportError(msg)

    @staticmethod
    def construct(lti_id, consumer_key, secret_key):
        """
        Contructs lti passport.
        """
        return ':'.join([lti_id, consumer_key, secret_key])

    def as_dict(self):
        return dict((prop, getattr(self, prop, None)) for prop in self.slots)

    def __str__(self):
        return LtiPassport.construct(self.lti_id, self.consumer_key, self.secret_key)

    def __unicode__(self):
        return unicode(str(self))


def get_simulation_id(uri):
    """
    Returns Simulation id extracted from the passed URI.
    """
    return urlparse(uri).path.strip('/').split('/')[-1]


def get_parent_unit(xblock):
    """
    Find a parent for the xblock.
    """
    while xblock:
        xblock = xblock.get_parent()
        if xblock is None:
            return None
        parent = xblock.get_parent()
        if parent is None:
            return None
        if parent.category == 'sequential':
            return xblock


def get_block_course_key(block):
    """
    Returns course key depending on block id type.
    """
    # The incoming block might be a CourseKey instance of some type, a
    # UsageKey instance of some type, or it might be something that has a
    # location attribute.  That location attribute will be a UsageKey
    identifier = getattr(block, 'id', None)
    if isinstance(identifier, CourseKey):
        course_key = block.id
    elif isinstance(identifier, UsageKey):
        course_key = block.id.course_key
    elif hasattr(block, 'location'):
        course_key = block.location.course_key
    else:
        course_key = None
    return course_key


def update_simulations(course_info, block, simulation_id):
    """
    Updates licensed simulations for block.
    """
    block_simulations = course_info.get(block)
    if not block_simulations and not isinstance(block_simulations, set):
        block_simulations = set()
    block_simulations.add(simulation_id)
    return block_simulations


def get_course_blocks_info(simulations):
    """
    Returns information about licensed simulations per block.
    """
    course_info = {}

    for simulation in simulations:
        simulation_id = get_simulation_id(simulation.launch_url)

        # we need to add blocks even if they do not have licensed simulations
        unit = get_parent_unit(simulation)
        if unit is None:
            log.debug('Cannot find ancestor for the xblock: %s', simulation)
            continue
        course_info[unit] = update_simulations(course_info, unit, simulation_id)
        subsection = unit.get_parent()
        if subsection is None:
            log.debug('Cannot find ancestor for the xblock: %s', unit)
            continue
        course_info[subsection] = update_simulations(course_info, subsection, simulation_id)
        chapter = subsection.get_parent()
        if chapter is None:
            log.debug('Cannot find ancestor for the xblock: %s', subsection)
            continue
        course_info[chapter] = update_simulations(course_info, chapter, simulation_id)

    return course_info


def validate_simulations_ids(course_key):
    """
    Validate simulations ids.
    """
    url_validator = URLValidator()
    sim_id_validator = RegexValidator(re.compile(r'^[a-zA-Z0-9]+$'), message=_('Enter a valid simulation id.'))
    errors = []
    valid_simulations = []

    lti_blocks = modulestore().get_items(course_key, qualifiers={'category': 'lti'})
    simulations = (block for block in lti_blocks if '/simulation/' in block.launch_url)
    for simulation in simulations:
        simulation_id = get_simulation_id(simulation.launch_url)

        for value, validator in ((simulation.launch_url, url_validator), (simulation_id, sim_id_validator)):
            try:
                validator(value)
                valid_simulations.append(simulation)
            except ValidationError as err:
                errors.append((simulation.display_name, simulation_id, u'<br>'.join(err.messages)))

    return valid_simulations, errors
