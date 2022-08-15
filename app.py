#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
from flask import Flask, render_template, request, flash, redirect, url_for, abort
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from forms import *
from flask_migrate import Migrate
from models import db, Artist, Venue, Show
from utils import format_artist_venue,  format_show, format_datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)

app.config.from_object('config')
app.jinja_env.filters['datetime'] = format_datetime
db.init_app(app)

migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.all()
  positions = {}
  data = []
  for venue in venues:
    past_shows = db.session.query(Show).join(Venue).filter(Show.venue_id == venue.id).filter(Show.start_time<datetime.now()).all()
    upcoming_shows = db.session.query(Show).join(Venue).filter(Show.venue_id == venue.id).filter(Show.start_time>datetime.now()).all()
    formatted_venue = format_artist_venue(venue, past_shows, upcoming_shows)
    formatted_venue["num_upcoming_shows"] = formatted_venue["upcoming_shows_count"]
    key = venue.city + venue.state
    if key in positions:
      data[positions[key]]["venues"].append(formatted_venue)
    else:
      data.append({
        "city": venue.city,
        "state": venue.state,
        "venues": [formatted_venue]
      })
      positions[key] = len(data) - 1

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get("search_term", "")
  venues = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()
  
  response={
    "count": len(venues),
    "data": venues
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  if not venue:
    return abort(404)
  
  past_shows = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id).filter(Show.start_time<datetime.now()).all()
  upcoming_shows = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id).filter(Show.start_time>datetime.now()).all()
  data = format_artist_venue(venue, past_shows, upcoming_shows)

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  try:
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    venue = Venue(name=form.name.data, genres=form.genres.data, address=form.address.data, city=form.city.data, state=form.state.data, phone=form.phone.data, website=form.website_link.data, facebook_link=form.facebook_link.data, seeking_talent=form.seeking_talent.data, seeking_description=form.seeking_description.data, image_link=form.image_link.data)
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + venue.name + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return redirect(url_for('show_venue', venue_id=venue.id))
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
    print(sys.exc_info())
    return redirect(url_for('create_venue_form'))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  error = False
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    print(error)
    if error == True:
      return abort(500)
    else:
      return 'deleted';




#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  
  return render_template('pages/artists.html', artists=Artist.query.all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get("search_term", "")
  data = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  if not artist:
    return abort(400)

  past_shows = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time<datetime.now()).all()
  upcoming_shows = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time>datetime.now()).all()
  data = format_artist_venue(artist, past_shows, upcoming_shows)

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist=Artist.query.get(artist_id)
  if not artist:
    return abort(404)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  if not artist:
    return abort(404)
  form = ArtistForm(request.form)
  # TODO: take values from the form submitted, and update existing
  artist.name = form.name.data
  artist.city = form.city.data
  artist.state = form.state.data
  artist.phone = form.phone.data
  artist.genres = form.genres.data
  artist.facebook_link = form.facebook_link.data
  artist.image_link = form.image_link.data
  artist.website = form.website_link.data
  artist.seeking_venue = form.seeking_venue.data
  artist.seeking_description = form.seeking_description.data
  try:
    db.session.commit()
    flash('Artist ' + str(artist.id) + ' was successfully updated!')
    # venue record with ID <venue_id> using the new attributes
    return redirect(url_for('show_artist', artist_id=artist.id))
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + str(artist.id) + ' could not be updated.')
    print(sys.exc_info())
    return redirect(url_for('edit_artist', artist_id=artist.id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id);
  if not venue:
    return abort(404)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  if not venue:
    return abort(404)
  form = VenueForm(request.form)
  # TODO: take values from the form submitted, and update existing
  venue.name = form.name.data
  venue.city = form.city.data
  venue.state = form.state.data
  venue.address = form.address.data
  venue.phone = form.phone.data
  venue.genres = form.genres.data
  venue.facebook_link = form.facebook_link.data
  venue.image_link = form.image_link.data
  venue.website = form.website_link.data
  venue.seeking_talent = form.seeking_talent.data
  venue.seeking_description = form.seeking_description.data
  try:
    db.session.commit()
    flash('Venue ' + str(venue.id) + ' was successfully updated!')
    # venue record with ID <venue_id> using the new attributes
    return redirect(url_for('show_venue', venue_id=venue.id))
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + str(venue.id) + ' could not be updated.')
    print(sys.exc_info())
    return redirect(url_for('edit_venue', venue_id=venue.id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  try:
    # TODO: insert form data as a new Venue record in the db, instead
    artist = Artist(name=form.name.data, genres=form.genres.data, city=form.city.data, state=form.state.data, phone=form.phone.data, website=form.website_link.data, facebook_link=form.facebook_link.data, seeking_venue=form.seeking_venue.data, seeking_description=form.seeking_description.data, image_link=form.image_link.data)
    db.session.add(artist)
    db.session.commit()
    # TODO: modify data to be the data object returned from db insertion
    # on successful db insert, flash success
    flash('Artist ' + artist.name + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., 
    return redirect(url_for('show_artist', artist_id=artist.id))
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
    print(sys.exc_info())
    return redirect(url_for('create_artist_form'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  for show in Show.query.all():
    data.append(format_show(show))
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)
  try:
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    show = Show(start_time=form.start_time.data, artist_id=form.artist_id.data, venue_id=form.venue_id.data)
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return redirect(url_for('shows'))
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
    print(sys.exc_info())
    return redirect(url_for('create_shows'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
