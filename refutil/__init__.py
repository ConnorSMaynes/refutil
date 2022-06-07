import weakref
import types
import functools

__all__ = [
	'reftype',
	'ref',
	'partial',
]


__version__ = '1.0.0'


def _weak_callback(wrcb, *args, **kwargs):
	# static method to resolve a weakref callable and try
	# to call it with the given args if still available
	cb = wrcb()
	if cb is None:
		return
	return cb(*args, **kwargs)


def _reftype_new(cls, obj, callback=None, **fields):
	"""Weakref to function, object, or method, with an optional callback
	of any of those types.
	
	Args:
		obj: A function, object, or method instance.
		callback: Optional. Callback to be called when obj about to be
			garbage collected. Method callbacks are automatically
			weakly referenced to avoid memory leak.
		**fields: Optional. Keyword arguments to fill in field values on init,
			when reference object created. Defaults to {}.
	
	Returns:
		A ReferenceType instance with the fields defined when the 
			reftype class was created.
	"""
	if isinstance(callback, types.MethodType):
		callback = partial(callback)
	if isinstance(obj, types.MethodType):
		rt = cls._method_ref_type
	else:
		rt = cls._ref_type
	inst = rt.__new__(rt, obj, callback)
	for k, v in fields.items():
		setattr(inst, k, v)
	return inst


def reftype(name, fields):
	"""Create a new, slotted, reference type with the given fields,
	which handles safely creating weak refs to any object type.
	
	Args:
		name: The name for the new type. ex: MyThingWeakReference
		fields: A list of field names to add to the reference type,
			which can be set and used by a callback later.

	Returns:
		A subclass of weakref.ref, which will generate the appropriate 
			reference object for the given object when called.
	"""
	if fields:
		attrs = dict(__slots__=fields)
		_ref_type = type(name + 'ObjectType', (weakref.ref,), attrs)
		_method_ref_type = type(name + 'MethodType', (weakref.WeakMethod,), attrs)
	else:
		_ref_type = weakref.ref
		_method_ref_type = weakref.WeakMethod
	return type(
			name,
			(weakref.ref,),
			dict(
				_ref_type=_ref_type,
				_method_ref_type=_method_ref_type,
				__new__=_reftype_new,
			),
		)


ref = reftype('', [])  # default ref type with no extra fields


def partial(callback, *args, **kwargs):
	"""Generate functools partial, but with a weak ref to the callable
	which will be resolved automatically or return None if ref lost.
	
	Args:
		callback: Callable to create a functools.partial for
		*args: Optional. Positional arguments to the `callback`
		**kwargs: Optional. Keyword-arguments to the `callback`
	
	Returns:
		functools.partial
	"""
	return functools.partial(
			_weak_callback,
			ref(callback),
			*args, **kwargs,
		)
