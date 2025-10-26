## -------------------------------------------------------------------------
## @author Leonardo Florez-Valencia (florez-l@javeriana.edu.co)
## -------------------------------------------------------------------------

import Ogre
import Ogre.Bites as OgreBites

"""
"""
class BaseListener( OgreBites.InputListener ):

  '''
  '''
  m_Root = None

  '''
  '''
  def __init__( self, root ):
    super( BaseListener, self ).__init__( )
    self.m_Root = root
  # end def

  '''
  '''
  def keyPressed( self, evt ):
    if evt.keysym.sym == OgreBites.SDLK_ESCAPE:
      self.m_Root.queueEndRendering( )
    # end if
    return True
  # end def
# end class

## eof - BaseListener.py
