// variables
// -------------------------------------

// - the div where we're located;
var _entryPoint; 

// - the minimum delay between a transition (it will surpass this if the load is taking longer)
var _minDelay;

// - the time it takes to fade between images
var _fadeOverTime;

// - the image array
var _images = [];

// - the game titles array
var _gameTitles = [];

// - current index
var _currentImageIndex;

// - the preloader, if one exists
var _preloader;

// - boolean, true if loading
var _loading = false;

// - boolean, if true then minDelay has passed
var _minDelayPassed = true;

// - boolean, if true then game titles are links
var _gameTitlesAreLinks = true;

// - counts the number of image loads
var _successCounter = 0;

// - the jsonp callback url
//var _imageCallbackUrl = 'http://localhost:8000/deadendthrills';
//var _imageCallbackUrl = 'http://teamwoods.org/deadendthrills/jsonp_callback=?';
var _imageCallbackUrl = 'http://localhost:8000/jsonp_callback=?';

// - CONSTS
var NOOF_IMAGES = 2;


// functions
// -------------------------------------

// - gets a new image url from offsite
function getNewImage(startMinDelay, imgIndex) 
{	
	_currentImageIndex = imgIndex;

	// get image url from jsonp	
	var jqxhr = $.getJSON(_imageCallbackUrl, function(json){data = json});
	jqxhr.success(successFunction);
	jqxhr.error(errorFunction);
	
	_loading = true;
}

// - the jsonp callback returned successfully
function successFunction()
{
	console.log("[deadendthrills] Loading " + data.url);
	$(_images[_currentImageIndex]).attr("src", data.url);
	_gameTitles[_currentImageIndex].html(data.name);
	
	if(_successCounter > 0)
	{
		_minDelayPassed = false;
		setTimeout(function()
		{
			_minDelayPassed = true;
			if(_loading == false)
				performTransition();
				
		},	_minDelay);
	}
	
	++_successCounter;
}

// - the jsonp callback returned an error
function errorFunction(XMLHttpRequest,textStatus, errorThrown) 
{
	console.log("An error occurred.");
}

// - creates a new img tag with the correct style
function createImage()
{
	var newImage =  document.createElement('img');
	newImage.onload = imageLoadedCallback;
	newImage.onerror = imageErrorCallback;
	$(newImage).attr("style","width:100%;display:none;position:absolute;");
	return newImage;
}

// - performs the transition
function performTransition()
{
	$(_images[_currentImageIndex])		.css({"display":"block", "opacity":"0"});
	$(_gameTitles[_currentImageIndex])	.css({"display":"block", "opacity":"0"});	
	
	for(var i = 0; i < NOOF_IMAGES; ++i)
	{	
		var index = i;
		$(_images[i]).animate(
		{
			opacity: i == _currentImageIndex ? 1 : 0,
			
		}, _fadeOverTime, function() 
			{
				if(this == _images[_currentImageIndex] && !_loading)
				{
					// anim complete - fetch the next image
					var nextImageIndex = _currentImageIndex + 1;
					if(nextImageIndex >= NOOF_IMAGES)
						nextImageIndex = 0;
					getNewImage(true, nextImageIndex);
				}
			}
		);
		
		$(_gameTitles[i]).animate({ opacity: i == _currentImageIndex ? 1 : 0 }, _fadeOverTime);
	}
}

// - call back once the image has loaded
function imageLoadedCallback(object)
{	
	_loading = false;
	
	if(_preloader != null)
	{
		$(_preloader).remove();
		_preloader = null;
	}
	
	if(_minDelayPassed)
		performTransition();
}

// - callback if the image load errors
function imageErrorCallback(object)
{	
	// try again
	getNewImage(true, _currentImageIndex);
}

// - [jQuery] the DOM is ready 
$(document).ready(function() 
{
	_entryPoint = document.getElementById("deadendthrills_slideshow");
	_minDelay = parseInt(_entryPoint.getAttribute("delay"), 10);
	_fadeOverTime = parseInt(_entryPoint.getAttribute("fadeover"), 10);
	
	_preloader = document.getElementById("deadendthrills_preloader");
		
	var innerDiv = document.createElement('div');
	$(innerDiv).attr("style","width:100%;margin:0px auto;");

	for(var i = 0; i < NOOF_IMAGES; ++i)
	{
		_images[i] = createImage();
		innerDiv.appendChild(_images[i]);
	}
	
	// check for gameTitle
	gameTitle = document.getElementById("deadendthrills_game_title");
	if(gameTitle != null)
	{
		ml = gameTitle.getAttribute("make_link");
		_gameTitlesAreLinks = !( ml != null && ( ml == "false" || ml == "0" ) );	
			
		for(var i = 0; i < NOOF_IMAGES; ++i)
		{
			_gameTitles[i] = $(gameTitle).clone()
			_gameTitles[i].css("display", "none");
			_gameTitles[i].html("Hello, World #" + (i+1));
			
			_gameTitles[i].appendTo(innerDiv);
		}
		$(gameTitle).remove();
	}
	
	_entryPoint.appendChild(innerDiv);
	
	getNewImage(false, 0);

});
