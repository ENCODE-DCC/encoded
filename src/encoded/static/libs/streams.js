var util = require('util');
var assert = require('assert');
var StringDecoder = require('string_decoder').StringDecoder;
var stream = require('stream');

// Gets delimited string data, and emits the parsed objects
var DelimitedStream = module.exports.DelimitedStream = function (options) {
  if (!(this instanceof DelimitedStream))
    return new DelimitedStream(options);

  stream.Transform.call(this, options);
  this._writableState.objectMode = false;
  this._readableState.objectMode = true;
  this._buffer = '';
  this.delimiter = options.delimiter || '\n'
  this._decoder = new StringDecoder('utf8');
}

util.inherits(DelimitedStream, stream.Transform);

DelimitedStream.prototype._transform = function(chunk, encoding, done) {
  this._buffer += this._decoder.write(chunk);
  // split on \0
  var items = this._buffer.split(this.delimiter);
  // keep the last partial message buffered
  this._buffer = items.pop();
  for (var i = 0; i < items.length; i++) {
    this.push(items[i]);
  }
  done();
};

DelimitedStream.prototype._flush = function(done) {
  assert.equal(this._buffer, '');
  done();
};

// SimpleTransform function transform(obj) -> obj
var SimpleTransform = module.exports.SimpleTransform = function (options) {
  if (!(this instanceof SimpleTransform))
    return new SimpleTransform(options);

  stream.Transform.call(this, options);
  this._writableState.objectMode = true;
  this._readableState.objectMode = true;
  this.transform = options.transform;
}

util.inherits(SimpleTransform, stream.Transform);

SimpleTransform.prototype._transform = function(obj, encoding, done) {
  try {
    this.push(this.transform(obj));
  } catch (err) {
    // Don't emit 'error' as it causes problems
    this.emit('error_result', err)
  }
  done();
};

// Output str as bytes
var OutputLength = module.exports.OutputLength = function (options) {
  if (!(this instanceof OutputLength))
    return new OutputLength(options);

  stream.Transform.call(this, options);
  options = options || {};
  this.result_type = options.result_type || 'RESULT';
  this._writableState.objectMode = true;
  this._readableState.objectMode = false;
}

util.inherits(OutputLength, stream.Transform);

OutputLength.prototype._transform = function(str, encoding, done) {
  var data = Buffer(str);
  this.push(this.result_type + ' ' + data.length + '\n');
  this.push(data.toString());
  done();
};


var StringIO = module.exports.StringIO = function(options) {
  if (!(this instanceof StringIO))
    return new StringIO(options);

  stream.Transform.call(this, options);
  this._raw = [];
}

util.inherits(StringIO, stream.Transform);

StringIO.prototype._write = function(chunk, encoding, done) {
  this._raw.push(chunk);
  done();
}

StringIO.prototype.getValue = function() {
  return Buffer.concat(this._raw).toString();
}

StringIO.prototype.clear = function() {
  return this._raw = [];
}

