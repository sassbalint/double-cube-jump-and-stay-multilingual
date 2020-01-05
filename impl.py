import sys
import fileinput
import json

# corpus lattice
cl_vertices_f = {} # freq of vertices
cl_vertices_l = {} # length of VCCs at vertices
cl_edges_back = {} # backward edges (= "in"-edges) down in cl
cl_edges_fwrd = {} # forward edges (= "out"-edges) up in cl

# fixed order (of slots) is important -- nothing to be done here for this
# what we do: always process dicts by sorted_keys{}
# input should be JSON dict indeed! :)
# remark: currently this is used only at very first load...
def json2dict( x ):
  j = None
  try:
    j = json.loads(x, encoding="utf-8")
  except ValueError as err:
    sys.stderr.write( "ValueError: {}".format( err ) + "{" + x + "}\n" )
    exit( 1 )
  return j

# keys of a dict in alphabetical order
def sorted_keys( d ):
  return sorted(d.keys())

# point: store dicts as JSON when used for key in dicts
# ensuring fixed order:
#   put keys and values into a list ordered by key: [ k1, v1, k2, v2 ... ]
def dict2jsonarray( x ):
  z = []
  keys = sorted_keys(x)
  for k in keys:
    z.append( k )
    z.append( x[k] )
  return json.dumps( z )

# input: vcc (as dict)
# output: length of vcc
def vcc_length( x ):
  return len(x.keys()) + len(list(filter(lambda x: x is not None,x.values())))

# from a vcc ('d') calculates vccs "shorter by 1" element ('e') recursively,
# and record the resulting edges and vertices
def build_dc_recursively( d, fq, vertices_f, vertices_l, edges_back, edges_fwrd ):
  slots = sorted_keys(d)
  dj = dict2jsonarray( d ) # vcc: dict format -> string format (= key!)

  # "shorter by 1" elements = every slot is to be shortened by 1 respectively
  for sl in slots:
    e = d.copy()
    if e[sl] is None: # if no filler -> omit the slot
      del e[sl]      
    else: # if filler -> omit the filler
      e[sl] = None
    ej = dict2jsonarray( e ) # vcc: dict format -> string format (= key!)

    # point: process every vertex exactly _once_,
    #        plus every edge from the given vertex -- OK!
    #        during building of cl handle vertices and edges at the same time
    #        (=> thus the structure must be traversed only once)
    #        edge values should be read from vertices -- this is completely OK!

    # -- enumerating edges = all edges needed starting form the given vertex
    #    data structure: 2x dict = dict according to startpoints
    #                    endpoints in dict (value = '1' if exists)
    #    XXX maybe: should be better with a set -- but OK for now :)
    if dj not in edges_back:
      edges_back[dj] = {}
    edges_back[dj][ej] = 1
    if ej not in edges_fwrd:
      edges_fwrd[ej] = {}
    edges_fwrd[ej][dj] = 1

    # -- enumerating vertices = vertices are needed only if not processed yet
    if ej not in vertices_f: # every vertex counted only once
                             # => every build_dc_recursively() step gets to
                             #    a given vertex only once!
                             # -- this implements the metric on the poster
      vertices_f[ej] = fq
      vertices_l[ej] = vcc_length( e )
      if len(e) > 0:
        build_dc_recursively( e, fq, vertices_f, vertices_l, edges_back, edges_fwrd )

# -----

# -- build the corpus lattice

for line in fileinput.input():
  d = json2dict(line)
  fq = d.pop('fq', None)

  # handling "NULL" lemmas, e.g. Hungarian "ACC":"NULL"
  # = definite conjugation means "ACC":"NULL"
  #   instead of this there we be a vcc "shorter by 1" = "ACC":None
  for k in d:
    if d[k] == "NULL":
      d[k] = None

  # adding subjects -- hack, because Hungarian is pro-drop
  # = if there is no NOM slot => add "NOM":None
  if "nsubj" not in d:
    d["nsubj"] = None

  # data for the given sentence skeleton (ss):
  dvfq = {} # vertex-data: freqs
  dvl = {}  # vertex-data: lengths
  de = {}   # edge-data
  deb = {}  # edge-data -- backwards!

  dj = dict2jsonarray( d ) # vcc: dict format -> string format (= key!)
    # XXX maybe: dj = line -- there would be no need for converting forth and back

  # put in the ss
  # XXX ugly: code repetition from build_dc_recursively()
  length = vcc_length( d )
  dvfq[dj] = fq
  dvl[dj] = length # = cnt of slots + cnt of fillers

  build_dc_recursively( d, fq, dvfq, dvl, de, deb )
  # algo: edges and vertices for each ss
  # plus: put together afterwards below -- THAT IS OK!

  # transfer vertices of the given ss into main 'cl_vertices_f': freqs
  for k in dvfq:
    if k not in cl_vertices_f:
      cl_vertices_f[k] = dvfq[k]
    else:
      cl_vertices_f[k] += dvfq[k]
  # transfer vertices of the given ss into main 'cl_vertices_l': vcc lengths
  for k in dvl:
    if k not in cl_vertices_l:
      cl_vertices_l[k] = dvl[k]
  # transfer edges of the given ss into main 'cl_edges_back'
  for i in de:
    for j in de[i]:
      if i not in cl_edges_back:
        cl_edges_back[i] = {}
      cl_edges_back[i][j] = 1
  # transfer edges of the given ss into main 'cl_edges_fwrd'
  for i in deb:
    for j in deb[i]:
      if i not in cl_edges_fwrd:
        cl_edges_fwrd[i] = {}
      cl_edges_fwrd[i][j] = 1

# -----

# idea #3: "jump and stay from root vertex"

STAY = 1.7       # below this  forward:stay
JMP1 = 4         # above this  backward:jump  (if keeping a filler)
JMP2 = 4         # above this  backward:jump  (if no filler)
JMP3 = 100000000 # above this  backward:jump  (if omitting last filler)
# 3. "full-free jump and stay" = 4,4,inf -> this is in the paper!
# 4. "refined jump and stay" = 4,9,100

def print_msg( msg ):
  print( " {0}".format( msg ) )

def print_simple( i ):
  fq = cl_vertices_f[i]
  l = cl_vertices_l[i]
  # current vertex
  print( "{0}\t{1}\t{2}".format( i, fq, l ))

def print_full( i ):
  fq = cl_vertices_f[i]

  # forward edges -- for "stay"
  if i in cl_edges_fwrd:
    d = cl_edges_fwrd[i]
    # sort: according to fq value, then vcc string-format key
    for j in sorted(d.keys(), key=lambda x: (cl_vertices_f[x],x)):
      ratio = fq/cl_vertices_f[j]
      cl = "??"
      if ratio < STAY:
        cl = "= !stay"
      if ratio > JMP1:
        cl = "^"
      print ( "->  {0}  {1:2.2f}  {2}  {3}".format(
              cl_vertices_f[j], ratio, j, cl ))
  print( "x" )

  # backward edges -- for "jump"
  if i in cl_edges_back:
    d = cl_edges_back[i]
    # sort: according to fq value, then vcc string-format key
    for j in sorted(d.keys(), key=lambda x: (cl_vertices_f[x],x)):
      ratio = cl_vertices_f[j]/fq
      cl = "??"
      if ratio < STAY:
        cl = "="
      if ratio > JMP1:
        cl = "^ !jump"
      print ( "<-  {0}  {1:2.2f}  {2}  {3}".format(
              cl_vertices_f[j], ratio, j, cl ))
  print( "x" )

  print_simple( i )

# fq-ratio on a..b edge (there must be an a..b edge!)
def ratio( a, b ):
  return cl_vertices_f[a]/cl_vertices_f[b]

# whether 'b' stays compared to 'a' (there must be an a..b edge!)
def is_stay( a, b, stay=STAY ):
  return ratio( a, b ) < stay

# whether 'a' jumps compared to 'b' (there must be an a..b edge!)
def is_jump( a, b, jump ):
  return ratio( a, b ) > jump

# whether there is a filler in x
def has_filler( x ):
  xx = json.loads(x, encoding="utf-8")
  values = xx[1::2]
  # this is a dict encoded as list by dict2jsonarray()
  # need to look at even elements (= values), whether there is a not-None
  return any( values ) # there is a not-False (None is False)

# whether 'x' is a ss
# XXX is this condition OK? "it has no forward edge" -- THINK ABOUT IT!
def is_top_of_cl( x ):
  return x not in cl_edges_fwrd

# take all vertices and filter out which is not needed
# point: not to miss any which is needed! :)

# process in a king of "good" order: 
# according to length, then reverse fq (by '-' trick), then alphabetical order
n = 1
for i in sorted(cl_vertices_f, key=lambda x: (cl_vertices_l[x],-cl_vertices_f[x],x)):

  print( "#{0}".format( n ) )
  n += 1

  print_full( i )

  # preliminary filter conditions -- THINK ABOUT IT!
  #  -- only if has out-edge
  #  -- only if fq >= 3
  #  -- only if l <= 8
  if i not in cl_edges_fwrd:
    print_msg( "No out-edge, skip." )
  elif ( cl_vertices_f[i] < 3 ):
    print_msg( "Too rare (<3), skip." )
  elif ( cl_vertices_l[i] > 8 ):
    print_msg( "Too long (>8), skip." )
  else:
    print_msg( "Processing." )
    d = cl_edges_fwrd[i] # forward edges -- is this line redundant? XXX

    # how does it work
    # 
    #  * is there a stay?
    #    -> perform the step defined by the smallest-ratio stay
    # 
    #  * if no stay, is there a jump?
    #    -> perform the step defined by the largest-ratio jump 
    #       iff there is a filler and there is a filler after the jump as well (JMP1)
    #           or there is no filler at all in the current vertex (JMP2)
    #
    #  * do it again if a step was made
    #
    # so it performs necessary amount of jumps and stays mixed
  
    act = i

    path = [] # = log of jumps and stays

    while True:
      stay_found = True
      jump_found = True

      # is there a stay?
      max_out = None
      d = cl_edges_fwrd.get( act, {} ) # forward vertices
                                       # there are always one except at a ss

      if d:
        max_out = max(d.keys(), key=lambda x: (cl_vertices_f[x],x))

      if max_out and is_stay( act, max_out ):
        print_msg( "A stay found, we follow." )
        path.append( 'v' )
        print_simple( max_out )
        act = max_out

      else:
        print_msg( "No stay (ratio={0:2.2f} > {1}), we stop.".format(
          ratio( act, max_out ) if max_out else 0, STAY ) )
        stay_found = False

        # if no stay, is there a(n appropriate) jump?
        max_inn = None
        d = cl_edges_back.get( act, {} ) # backward vertices
                                         # there are always one except at root

        if d:
          max_inn = max(d.keys(), key=lambda x: (cl_vertices_f[x],x))

        if max_inn: # this exists except at root :)
          r = ratio( max_inn, act )
          jump = None
          info_msg = None
          jump_type = None

          # 3 different cases which covers all possibilities
          # xor: there is a filler and there is a filler after the jump as well
          if has_filler( max_inn ):
            jump = JMP1
            info_msg = "keeping a filler"
            jump_type = "t(k)"
          # xor: there is no filler at all in the current vertex
          elif not has_filler( act ):
            jump = JMP2
            info_msg = "no filler"
            jump_type = "t(n)"
          # xor: there is one filler and the jump omits it
          elif has_filler( act ) and not has_filler( max_inn ):
            jump = JMP3
            info_msg = "omitting last filler"
            jump_type = "t(o)"
          else:
            print_msg( "impossible outcome" ) # as we covered all possibilities
            exit( 1 )

          # check whether the jump is OK
          if is_jump( max_inn, act, jump ):
            print_msg( "An appropriate jump ({0}, {1}<) found, we follow.".format( info_msg, jump ) )
            path.append( jump_type )
            print_simple( max_inn )
            act = max_inn
          else:
            print_msg( "No appropriate jump ({0}, {1:2.2f} < {2}), we stop.".format( info_msg, r, jump ) )
            jump_found = False

        else:
          print_msg( "No backward edge -- no jump, we stop." ) # at root vertex
          jump_found = False

      # quit the loop when no step was made
      if not stay_found and not jump_found: break

    # what to do when we are at an ss
    # current implementation: no ss can be a pVCC -- THINK ABOUT IT!
    # because there are pVCCS like 'shine sun'
    if ( is_top_of_cl( act ) ):
      print_msg( "Concrete sentence skeleton." )

    else:
      #pathstr = '0' if not path else ''.join( path )
      #print( "{0}\t{1}\t{2}\t[{3}]\tpVCC".format( act, cl_vertices_f[act], cl_vertices_l[act], pathstr ))
      print( "{0}\t{1}\t{2}\tpVCC".format( act, cl_vertices_f[act], cl_vertices_l[act] ))
  print()

