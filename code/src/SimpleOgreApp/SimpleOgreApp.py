## -------------------------------------------------------------------------
## @author Leonardo Florez-Valencia (florez-l@javeriana.edu.co)
## @author Alejandro Caicedo (caicedo_alejandro@javeriana.edu.co)
## -------------------------------------------------------------------------

import os, sys, math, random, vtk
cur_dir = os.path.dirname( os.path.abspath( __file__ ) )
imp_dir = os.path.abspath( os.path.join( cur_dir, '../../lib' ) )
sys.path.append( imp_dir )
import Ogre, PUJ_Ogre
import Ogre.Bites as OgreBites

class MyPowerfulCameraMan( OgreBites.CameraMan ):
  def __init__( self, node ):
    super( MyPowerfulCameraMan, self ).__init__( node )
  # end def
# end class

class ProjectileInputListener( OgreBites.InputListener ):
  def __init__( self, app ):
    super( ProjectileInputListener, self ).__init__( )
    self._app = app
  # end def

  def mousePressed( self, evt ):
    if evt.button == OgreBites.BUTTON_LEFT:
      self._app._spawnProjectile( )
    # end if
    return True
  # end def
# end class

"""
"""
class SimpleOgreApp( PUJ_Ogre.BaseApplication ):

  '''
  '''
  m_CamMan = None

  '''
  '''
  def __init__( self ):
    super( SimpleOgreApp, self ).__init__( 'SimpleOgreApp v0.1', '' )
    self.m_ResourcesFile = os.path.join( cur_dir, 'resources.cfg' )
    self._projectiles = [ ]
    self._projectile_speed = 30.0
    self._projectile_lifetime = 3.0
    self._projectile_index = 0
    self._root_node = None
    self._camera = None
    self._projectile_listener = ProjectileInputListener( self )
    self._spawn_timer = 0.0
    self._spawn_interval_range = ( 2.0, 5.0 )
    self._next_spawn_delay = random.uniform( *self._spawn_interval_range )
    self._spawn_offset_range = {
      'x': ( -5.0, 5.0 ),
      'y': ( -0.5, 2.0 ),
      'z': ( -5.0, 5.0 )
    }
    self._spawned_spheres = [ ]
    self._spawn_index = 0
    self._eye_move_speed = 4.0
    self._eye_stop_distance = 1.0
    self._eye_min_spawn_distance = 5.0 # Min distance from camera to spawn eye spheres
  # end def

  '''
  '''
  def _loadScene( self ):

    # Get root and create scene manager
    win = self.getRenderWindow( )
    root = self.getRoot( )
    root_node = self.m_SceneMgr.getRootSceneNode( )
    self._root_node = root_node

    # Configure camera
    cam = self.m_SceneMgr.createCamera( 'MainCamera' )
    cam.setNearClipDistance( 0.005 )
    cam.setAutoAspectRatio( True )

    camnode = root_node.createChildSceneNode( )
    camnode.setPosition( [ 0, 1.7, 15 ] )

    camnode.lookAt( [ 0, 0, 0 ], Ogre.Node.TS_WORLD )
    camnode.attachObject( cam )
    self._camera = cam

    self.m_CamMan = MyPowerfulCameraMan( camnode )
    self.m_CamMan.setStyle( OgreBites.CS_FREELOOK )
    self.m_CamMan.setTopSpeed( 10 )
    self.m_CamMan.setFixedYaw( True )
    self.addInputListener( self.m_CamMan )
    self.addInputListener( self._projectile_listener )

    # Configure viewport
    vp = win.addViewport( cam )
    vp.setBackgroundColour( Ogre.ColourValue( 0.9, 0.75, 0.5 ) )

    # Light
    light = self.m_SceneMgr.createLight( 'MainLight' )
    light.setType( Ogre.Light.LT_DIRECTIONAL )
    light_node = root_node.createChildSceneNode( )
    light_node.attachObject( light )
    light_node.setDirection( [ -0.5, -1, -0.5 ], Ogre.Node.TS_WORLD )

    # Load a mesh
    ent = self.m_SceneMgr.createEntity( 'Sinbad', 'Sinbad.mesh' )
    node = root_node.createChildSceneNode( )
    node.attachObject( ent )
    node.setPosition( 0, 8, 0 )

    ent = self.m_SceneMgr.createEntity( 'C_Chusma', 'C_Chusma.mesh' )
    node = root_node.createChildSceneNode( )
    node.attachObject( ent )
    node.setPosition( 0, 1, 0 )

    ent = self.m_SceneMgr.createEntity( 'C_Chusma_LTra', 'C_Chusma_LTra.mesh' )
    node = root_node.createChildSceneNode( )
    node.attachObject( ent )
    node.setPosition( 0, -0.5, -1 )
    
    plane = Ogre.Plane( 0, 1, 0, 0.0 )
    planePtr = Ogre.MeshManager.getSingleton().createPlane(
        "ground",
        "General",
        plane,
        1500, 1500,
        20, 20,
        True,
        1,
        5, 5,
        [ 0, 0, 1 ]
       )
    ent = self.m_SceneMgr.createEntity("GroundEntity", "ground")
    ent.setMaterialName("tierra")
    node = root_node.createChildSceneNode( )
    node.attachObject( ent )
    
    vsphere = vtk.vtkSphereSource( )
    vsphere.SetRadius( 3 )
    vsphere.SetThetaResolution( 100 )
    vsphere.SetPhiResolution( 100 )
    vsphere.Update( )
    
    man = self.m_SceneMgr.createManualObject("target1")
    man.begin("pelota", Ogre.RenderOperation.OT_TRIANGLE_LIST)
    
    for i in range( vsphere.GetOutput( ).GetNumberOfPoints( ) ):
      pos = vsphere.GetOutput( ).GetPoint( i )
      man.position( pos )
    # end for

    for i in range( vsphere.GetOutput( ).GetNumberOfCells( ) ):
      cell = vsphere.GetOutput( ).GetCell( i )
      if cell.GetNumberOfPoints( ) == 3:
        man.triangle( cell.GetPointId( 0 ), cell.GetPointId( 1 ), cell.GetPointId( 2 ) )
      # end if
    # end for
    
    
    man.end( )
    node = root_node.createChildSceneNode( )
    node.attachObject( man )
    
  def _correctCamera( self ):
    pos = self.m_CamMan.getCamera( ).getPosition( )
    pos.y = 1.7
    self.m_CamMan.getCamera( ).setPosition( pos )
  # end def

  def _spawnProjectile( self ):
    cam = self._camera
    if cam is None or self._root_node is None:
      return
    direction = cam.getDerivedDirection( ).normalisedCopy( )
    origin = cam.getDerivedPosition( ) + direction * 0.5  # half a meter in front of the camera
    name = f"Projectile_{self._projectile_index}"
    self._projectile_index += 1
    entity = self.m_SceneMgr.createEntity( name, Ogre.SceneManager.PT_SPHERE )
    entity.setMaterialName( "pelota" )
    node = self._root_node.createChildSceneNode( name + "_node" )
    node.setScale( 0.0005, 0.0005, 0.0005 )
    node.setPosition( origin )
    node.attachObject( entity )
    velocity = direction * self._projectile_speed
    self._projectiles.append( {
      'node': node,
      'entity': entity,
      'velocity': velocity,
      'ttl': self._projectile_lifetime
    } )
  # end def

  def _updateProjectiles( self, dt ):
    alive = [ ]
    for data in self._projectiles:
      data[ 'ttl' ] -= dt
      if data[ 'ttl' ] <= 0:
        self._destroyProjectile( data )
        continue
      displacement = data[ 'velocity' ] * dt
      data[ 'node' ].translate( displacement, Ogre.Node.TS_WORLD )
      alive.append( data )
    # end for
    self._projectiles = alive
  # end def

  def _destroyProjectile( self, data ):
    node = data.get( 'node' )
    entity = data.get( 'entity' )
    if node is not None:
      node.detachAllObjects( )
      self.m_SceneMgr.destroySceneNode( node.getName( ) )
    # end if
    if entity is not None:
      self.m_SceneMgr.destroyEntity( entity )
    # end if
  # end def

  def _spawnSphere( self ):
    if self._root_node is None:
      return
    name = f"SpawnedSphere_{self._spawn_index}"
    self._spawn_index += 1
    entity = self.m_SceneMgr.createEntity( name, Ogre.SceneManager.PT_SPHERE )
    entity.setMaterialName( "eye_sphere" )
    node = self._root_node.createChildSceneNode( name + "_node" )
    sx = random.uniform( 0.016, 0.03 )
    node.setScale( sx, sx, sx )
    base_pos = [ 0.0, 1.7, 0.0 ]
    if self._camera is not None:
      cam_pos = self._camera.getDerivedPosition( )
      base_pos = [ cam_pos.x, cam_pos.y, cam_pos.z ]
    # Slight randomness keeps spheres near the player without overlapping
    min_dist = self._eye_min_spawn_distance
    target_pos = None
    offset = None
    # Makes sure the spawned sphere is at least min_dist away from the base_pos
    for _ in range( 10 ):
      candidate = [
        base_pos[ 0 ] + random.uniform( *self._spawn_offset_range[ 'x' ] ),
        max( 0.5, base_pos[ 1 ] + random.uniform( *self._spawn_offset_range[ 'y' ] ) ),
        base_pos[ 2 ] + random.uniform( *self._spawn_offset_range[ 'z' ] )
      ]
      offset = [
        candidate[ 0 ] - base_pos[ 0 ],
        candidate[ 1 ] - base_pos[ 1 ],
        candidate[ 2 ] - base_pos[ 2 ]
      ]
      distance = math.sqrt( offset[ 0 ] ** 2 + offset[ 1 ] ** 2 + offset[ 2 ] ** 2 )
      if distance >= min_dist:
        target_pos = candidate
        break
    # end for
    if target_pos is None:
      if offset is None or ( offset[ 0 ] == 0 and offset[ 1 ] == 0 and offset[ 2 ] == 0 ):
        offset = [ 1.0, 0.0, 0.0 ]
      dir_vec = Ogre.Vector3( offset[ 0 ], offset[ 1 ], offset[ 2 ] )
      if dir_vec.length( ) == 0:
        dir_vec = Ogre.Vector3( 1.0, 0.0, 0.0 )
      dir_vec = dir_vec.normalisedCopy( )
      base_vec = Ogre.Vector3( base_pos[ 0 ], base_pos[ 1 ], base_pos[ 2 ] )
      desired = base_vec + dir_vec * min_dist
      target_pos = [ desired.x, max( 0.5, desired.y ), desired.z ]
    # end if
    node.setPosition( target_pos )
    node.attachObject( entity )
    self._orientEyeNode( node )
    self._spawned_spheres.append( {
      'node': node,
  'entity': entity,
  'speed': self._eye_move_speed,
      'stop_distance': self._eye_stop_distance
    } )
  # end def

  def _orientEyeNode( self, node ):
    if node is None or self._camera is None:
      return
    cam_pos = self._camera.getDerivedPosition( )
    node_pos = node._getDerivedPosition( )
    look_dir = ( cam_pos - node_pos )
    if look_dir.length( ) == 0:
      return
    look_dir = look_dir.normalisedCopy( )
    up = Ogre.Vector3( 0, 1, 0 )
    if abs( look_dir.dotProduct( up ) ) > 0.99:
      up = Ogre.Vector3( 0, 0, 1 )
    right = look_dir.crossProduct( up )
    if right.length( ) == 0:
      return
    right = right.normalisedCopy( )
    corrected_up = right.crossProduct( look_dir ).normalisedCopy( )
    orientation = Ogre.Quaternion( )
    orientation.FromAxes( right, corrected_up, -look_dir )
    node.setOrientation( orientation )
  # end def

  def _updateEyeSpheres( self, dt ):
    if self._camera is None:
      return
    cam_pos = self._camera.getDerivedPosition( )
    for data in self._spawned_spheres:
      node = data.get( 'node' )
      if node is None:
        continue
      node_pos = node._getDerivedPosition( )
      direction = cam_pos - node_pos
      distance = direction.length( )
      stop_distance = data.get( 'stop_distance', self._eye_stop_distance )
      if distance > stop_distance and distance > 0:
        direction = direction.normalisedCopy( )
        move_speed = data.get( 'speed', self._eye_move_speed )
        step = min( move_speed * dt, max( 0.0, distance - stop_distance ) )
        if step > 0:
          displacement = direction * step
          node.translate( displacement, Ogre.Node.TS_WORLD )
          node_pos = node._getDerivedPosition( )
          direction = cam_pos - node_pos
      # end if
      self._orientEyeNode( node )
    # end for
  # end def

  def _updateSpawner( self, dt ):
    # Spawn spheres once the timer reaches the next randomized delay
    self._spawn_timer += dt
    while self._spawn_timer >= self._next_spawn_delay:
      self._spawnSphere( )
      self._spawn_timer -= self._next_spawn_delay
      self._next_spawn_delay = random.uniform( *self._spawn_interval_range )
    # end while
  # end def

  def frameRenderingQueued( self, evt ):
    if not super( SimpleOgreApp, self ).frameRenderingQueued( evt ):
      return False
    dt = evt.timeSinceLastFrame
    self._updateProjectiles( dt )
    self._updateSpawner( dt )
    self._updateEyeSpheres( dt )
    return True
  # end def
# end class

"""
"""
def main( argv ):
  app = SimpleOgreApp( )
  app.go( )
# end def

if __name__ == '__main__':
  main( sys.argv )
# end def

## eof - SimpleOgreApp.py
