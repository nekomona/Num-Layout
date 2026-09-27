; Numeric layout assist for Virtuoso IC23.1.
; J sets Path/Wire width, Stretch extent, or Move displacement.
; Shift-J sets the displacement magnitude of Move/Stretch.

when(boundp('vbnInstalled) && vbnInstalled
  vbnUninstall()
)

vbnToolbarGeneration = if(boundp('vbnToolbarGeneration) then
  vbnToolbarGeneration+1 else 1)

vbnInstalled = nil
vbnActive = nil
vbnWindow = nil
vbnCommand = nil
vbnKind = nil
vbnForm = nil
vbnDigits = ""
vbnNumber = nil
vbnEdges = nil
vbnHilight = nil
vbnHilightLabel = nil
vbnLastPoint = nil
vbnLastText = nil
vbnSavedKeys = nil
vbnMainOld = nil
vbnShiftOld = nil
vbnEnabled = t
vbnToolbar = nil
vbnAction = nil
vbnToolbarWindows = nil
vbnHoverSet = nil
vbnSelectedSet = nil
vbnPreviewSet = nil
vbnHoverObjects = nil
vbnSelectedObjects = nil
vbnPreviewObjects = nil
vbnLastValue = nil
vbnLastEdges = nil
vbnLastSnapMode = nil
vbnLastScreenPoint = nil
vbnPixelScale = nil
vbnPixelScaleView = nil

procedure(vbnX(p) car(p))
procedure(vbnY(p) cadr(p))
procedure(vbnPoint(x y) list(x y))

procedure(vbnGrid()
  let((cv tf grid)
    cv = when(vbnWindow geGetEditCellView(vbnWindow))
    tf = when(cv techGetTechFile(ddGetObj(cv~>libName)))
    grid = when(tf techGetMfgGridResolution(tf))
    if(numberp(grid) && grid > 0.0 then grid else 0.001)
  )
)

procedure(vbnSnap(x)
  let((grid)
    grid = vbnGrid()
    grid*floor(x/grid+0.5)
  )
)

procedure(vbnLinearTarget(fixed moving current value)
  let((dx dy oldDx oldDy magnitude)
    current = vbnConstrainPoint(fixed current)
    dx = vbnX(current)-vbnX(fixed)
    dy = vbnY(current)-vbnY(fixed)
    oldDx = vbnX(moving)-vbnX(fixed)
    oldDy = vbnY(moving)-vbnY(fixed)
    magnitude = sqrt(dx*dx+dy*dy)
    when(magnitude <= 0.0
      dx = oldDx dy = oldDy
      magnitude = sqrt(dx*dx+dy*dy))
    when(magnitude > 0.0
      vbnPoint(vbnSnap(vbnX(fixed)+value*dx/magnitude)
               vbnSnap(vbnY(fixed)+value*dy/magnitude)))
  )
)

procedure(vbnClearObjects(objects)
  foreach(obj objects when(obj geDeleteHilightObject(obj)))
  nil
)

procedure(vbnLine(set points)
  let((box ll ur stroke)
    when(set
      box = hiGetViewBBox(vbnWindow)
      ll = car(box) ur = cadr(box)
      stroke = max(2.0*vbnGrid()
                   max(vbnX(ur)-vbnX(ll) vbnY(ur)-vbnY(ll))/300.0)
      geAddHilightPath(set points stroke))
  )
)

procedure(vbnSegmentContour(set a b width)
  let((dx dy mag nx ny)
    dx = vbnX(b)-vbnX(a) dy = vbnY(b)-vbnY(a)
    mag = sqrt(dx*dx+dy*dy)
    if(!numberp(width) || width <= 0.0 || mag <= 0.0 then
      vbnLine(set list(a b))
    else
      nx = -dy/mag*width/2.0 ny = dx/mag*width/2.0
      vbnLine(set list(
        vbnPoint(vbnX(a)+nx vbnY(a)+ny)
        vbnPoint(vbnX(b)+nx vbnY(b)+ny)
        vbnPoint(vbnX(b)-nx vbnY(b)-ny)
        vbnPoint(vbnX(a)-nx vbnY(a)-ny)
        vbnPoint(vbnX(a)+nx vbnY(a)+ny)))
    )
  )
)

procedure(vbnBoxLine(set box)
  let((edges objects)
    edges = vbnBoxEdges(box)
    objects = nil
    foreach(edge edges objects = cons(vbnLine(set edge) objects))
    objects
  )
)

procedure(vbnArrow(a b)
  let((dx dy mag size ux uy tip left right)
    dx = vbnX(b)-vbnX(a)
    dy = vbnY(b)-vbnY(a)
    mag = sqrt(dx*dx+dy*dy)
    when(mag > 0.0
      ux = dx/mag uy = dy/mag
      size = min(mag/3.0 max(0.25 mag/18.0))
      tip = b
      left = vbnPoint(vbnX(tip)-size*ux+size*uy/2.0
                      vbnY(tip)-size*uy-size*ux/2.0)
      right = vbnPoint(vbnX(tip)-size*ux-size*uy/2.0
                       vbnY(tip)-size*uy+size*ux/2.0)
      vbnSelectedObjects = cons(vbnLine(vbnSelectedSet list(a b)) vbnSelectedObjects)
      vbnSelectedObjects = cons(vbnLine(vbnSelectedSet list(left tip right)) vbnSelectedObjects)
    )
  )
)

procedure(vbnDistanceToSegment(pt seg)
  let((a b dx dy length2 u qx qy)
    a = car(seg)
    b = cadr(seg)
    dx = vbnX(b) - vbnX(a)
    dy = vbnY(b) - vbnY(a)
    length2 = dx*dx + dy*dy
    if(length2 <= 0.0 then
      sqrt((vbnX(pt)-vbnX(a))**2 + (vbnY(pt)-vbnY(a))**2)
    else
      u = ((vbnX(pt)-vbnX(a))*dx + (vbnY(pt)-vbnY(a))*dy) / length2
      u = max(0.0 min(1.0 u))
      qx = vbnX(a) + u*dx
      qy = vbnY(a) + u*dy
      sqrt((vbnX(pt)-qx)**2 + (vbnY(pt)-qy)**2)
    )
  )
)

procedure(vbnEdgeLength(seg)
  let((a b)
    a = car(seg)
    b = cadr(seg)
    sqrt((vbnX(b)-vbnX(a))**2 + (vbnY(b)-vbnY(a))**2)
  )
)

procedure(vbnParallel(a b)
  let((p q r s cross)
    p = car(a) q = cadr(a) r = car(b) s = cadr(b)
    cross = (vbnX(q)-vbnX(p))*(vbnY(s)-vbnY(r)) -
            (vbnY(q)-vbnY(p))*(vbnX(s)-vbnX(r))
    abs(cross) <= 0.01*vbnEdgeLength(a)*vbnEdgeLength(b)
  )
)

procedure(vbnParallelDistance(a b)
  let((p q r)
    p = car(a) q = cadr(a) r = car(b)
    abs((vbnX(q)-vbnX(p))*(vbnY(r)-vbnY(p)) -
        (vbnY(q)-vbnY(p))*(vbnX(r)-vbnX(p))) / vbnEdgeLength(a)
  )
)

procedure(vbnBoxEdges(box)
  let((ll ur p1 p2 p3 p4)
    ll = car(box) ur = cadr(box)
    p1 = vbnPoint(vbnX(ll) vbnY(ll))
    p2 = vbnPoint(vbnX(ur) vbnY(ll))
    p3 = vbnPoint(vbnX(ur) vbnY(ur))
    p4 = vbnPoint(vbnX(ll) vbnY(ur))
    list(list(p1 p2) list(p2 p3) list(p3 p4) list(p4 p1))
  )
)

procedure(vbnPolygonEdges(points)
  let((work edges)
    work = points
    edges = nil
    while(cdr(work)
      edges = cons(list(car(work) cadr(work)) edges)
      work = cdr(work)
    )
    when(points && cdr(points) && !equal(car(last(points)) car(points))
      edges = cons(list(car(last(points)) car(points)) edges)
    )
    edges
  )
)

procedure(vbnWireWidthEdge(fig pt)
  let((begin end boundary dx dy magnitude nx ny offset low high projection u center)
    begin = fig~>beginPt end = fig~>endPt
    boundary = fig~>boundary
    when(begin && end && boundary
      dx = vbnX(end)-vbnX(begin)
      dy = vbnY(end)-vbnY(begin)
      magnitude = sqrt(dx*dx+dy*dy)
      when(magnitude > 0.0
        nx = -dy/magnitude ny = dx/magnitude
        low = nil high = nil
        foreach(vertex boundary
          offset = (vbnX(vertex)-vbnX(begin))*nx +
                   (vbnY(vertex)-vbnY(begin))*ny
          low = if(numberp(low) then min(low offset) else offset)
          high = if(numberp(high) then max(high offset) else offset)
        )
        when(numberp(low) && numberp(high) && high > low
          projection = ((vbnX(pt)-vbnX(begin))*dx +
                        (vbnY(pt)-vbnY(begin))*dy)/(magnitude*magnitude)
          u = max(0.0 min(1.0 projection))
          center = vbnPoint(vbnX(begin)+u*dx vbnY(begin)+u*dy)
          list(vbnPoint(vbnX(center)+low*nx vbnY(center)+low*ny)
               vbnPoint(vbnX(center)+high*nx vbnY(center)+high*ny))
        )
      )
    )
  )
)

procedure(vbnRawPointForWire(win adjusted fig)
  let((screen view ll ur dx dy denom numerator scale bbox screenWidth)
    screen = hiGetScreenPoint(win)
    view = hiGetViewBBox(win)
    when(screen && view
      ll = car(view) ur = cadr(view)
      dx = vbnX(fig~>endPt)-vbnX(fig~>beginPt)
      dy = vbnY(fig~>endPt)-vbnY(fig~>beginPt)
      denom = vbnX(screen)*dx-vbnY(screen)*dy
      numerator = (vbnX(adjusted)-vbnX(ll))*dx +
                  (vbnY(adjusted)-vbnY(ur))*dy
      scale = when(abs(denom) > 0.01
        numerator/denom)
      bbox = hiGetAbsWindowScreenBBox(win)
      screenWidth = vbnX(cadr(bbox))-vbnX(car(bbox))
      when(!numberp(scale) || scale <= 0.0 ||
           scale < (vbnX(ur)-vbnX(ll))/screenWidth ||
           (equal(view vbnPixelScaleView) && numberp(vbnPixelScale) &&
            abs(scale-vbnPixelScale) > 0.2*vbnPixelScale)
        scale = if(equal(view vbnPixelScaleView) then vbnPixelScale else nil))
      when(numberp(scale)
        vbnPixelScale = scale
        vbnPixelScaleView = view
        vbnPoint(vbnX(ll)+vbnX(screen)*scale
                 vbnY(ur)-vbnY(screen)*scale))
    )
  )
)

procedure(vbnFigureEdges(fig)
  let((typ points work edges)
    typ = fig~>objType
    cond(
      ((typ == "pathSeg" && fig~>boundary)
        vbnPolygonEdges(fig~>boundary))
      ((typ == "path" || typ == "polygon" || typ == "ruler")
        points = fig~>points
        if(typ == "polygon" then
          edges = vbnPolygonEdges(points)
        else
          work = points
          while(cdr(work)
            edges = cons(list(car(work) cadr(work)) edges)
            work = cdr(work)
          )
        )
        if(edges then edges else vbnBoxEdges(fig~>bBox)))
      (t vbnBoxEdges(fig~>bBox))
    )
  )
)

procedure(vbnPickEdge(win pt)
  let((cv view ll ur tolerance region figures best bestDistance distance
       centerPick centerDistance widthEdge width pickPoint)
    cv = geGetEditCellView(win)
    view = hiGetViewBBox(win)
    ll = car(view) ur = cadr(view)
    tolerance = max(0.01 (vbnX(ur)-vbnX(ll))/100.0)
    region = list(vbnPoint(vbnX(pt)-tolerance vbnY(pt)-tolerance)
                  vbnPoint(vbnX(pt)+tolerance vbnY(pt)+tolerance))
    ; Rulers are markers, not shapes returned by dbGetOverlaps.
    figures = dbGetOverlaps(cv region)
    foreach(marker cv~>markers
      when(marker~>objType == "ruler"
        figures = cons(marker figures)
      )
    )
    best = nil
    bestDistance = tolerance
    centerPick = nil
    centerDistance = tolerance
    foreach(fig figures
      when(dbIsId(fig) && fig~>bBox
        pickPoint = pt
        when(fig~>objType == "pathSeg"
          pickPoint = vbnRawPointForWire(win pt fig)
          unless(pickPoint pickPoint = pt)
          widthEdge = vbnWireWidthEdge(fig pickPoint)
          when(widthEdge
            width = vbnEdgeLength(widthEdge)
            distance = vbnDistanceToSegment(pickPoint
                         list(fig~>beginPt fig~>endPt))
            when(distance <= min(tolerance
                                 max(0.3*width
                                     if(numberp(vbnPixelScale) then
                                       0.5*vbnPixelScale else 0.0))) &&
                 distance <= centerDistance
              centerPick = widthEdge
              centerDistance = distance)
          )
        )
        foreach(edge vbnFigureEdges(fig)
          distance = vbnDistanceToSegment(pickPoint edge)
          when(vbnEdgeLength(edge) > 0.0 && distance <= bestDistance
            best = edge
            bestDistance = distance
          )
        )
      )
    )
    if(centerPick then centerPick else best)
  )
)

procedure(vbnCurrentValue()
  if(vbnEdges then vbnNumber
  else
    if(vbnDigits == "" || vbnDigits == "." then nil
    else atof(vbnDigits))
  )
)

procedure(vbnDisplayText()
  let((value)
    value = vbnCurrentValue()
    cond(
      (vbnEdges
        sprintf(nil "%0.6g  [%d edge%s]" value length(vbnEdges)
          if(length(vbnEdges) == 1 then "" else "s")))
      (vbnDigits != "" vbnDigits)
      (t if(vbnKind == 'width then "WIDTH"
         else if(vbnKind == 'length then "LENGTH"
         else if(vbnKind == 'wire then "WIRE WIDTH" else "DISTANCE"))))
    )
  )
)

procedure(vbnDrawPreview(pt value)
  let((start direction dx dy a b nx ny half selection fig box ll ur axis sign
       fixed moving points selectedPoints target)
    when(numberp(value)
      start = vbnEnteredStartPoint()
      direction = vbnDirection()
      cond(
        (vbnKind == 'width && start && pt
          dx = vbnX(pt)-vbnX(start) dy = vbnY(pt)-vbnY(start)
          half = sqrt(dx*dx+dy*dy)
          when(half > 0.0
            nx = -dy/half*value/2.0 ny = dx/half*value/2.0
            vbnPreviewObjects = cons(vbnLine(vbnPreviewSet
                list(vbnPoint(vbnX(start)+nx vbnY(start)+ny)
                     vbnPoint(vbnX(pt)+nx vbnY(pt)+ny)
                     vbnPoint(vbnX(pt)-nx vbnY(pt)-ny)
                     vbnPoint(vbnX(start)-nx vbnY(start)-ny)
                     vbnPoint(vbnX(start)+nx vbnY(start)+ny)))
              vbnPreviewObjects)
          ))
        (vbnKind == 'wire
          when(start && pt
            vbnPreviewObjects = cons(vbnSegmentContour(vbnPreviewSet start pt value)
                                      vbnPreviewObjects)))
        (vbnKind == 'distance && direction
          selection = geGetSelSet(vbnWindow)
          foreach(fig selection
            box = fig~>bBox
            when(box
              ll = car(box) ur = cadr(box)
              dx = vbnSnap(value*car(direction))
              dy = vbnSnap(value*cadr(direction))
              vbnPreviewObjects = append(vbnBoxLine(vbnPreviewSet
                list(vbnPoint(vbnX(ll)+dx vbnY(ll)+dy)
                     vbnPoint(vbnX(ur)+dx vbnY(ur)+dy)))
                vbnPreviewObjects))))
        (vbnKind == 'length && start && pt
          fig = car(geGetSelSet(vbnWindow))
          when(fig && length(geGetSelSet(vbnWindow)) == 1
            selectedPoints = geGetSelSetFigPoint(fig)
            if((fig~>objType == "path" || fig~>objType == "ruler") &&
               length(fig~>points) == 2 && length(selectedPoints) == 2 then
              points = fig~>points
              fixed = if(car(selectedPoints) then cadr(points) else car(points))
              moving = if(car(selectedPoints) then car(points) else cadr(points))
              target = vbnLinearTarget(fixed moving pt value)
              when(target
                vbnPreviewObjects = cons(vbnSegmentContour(vbnPreviewSet fixed target
                                             fig~>width)
                                          vbnPreviewObjects))
            else
              box = fig~>bBox ll = car(box) ur = cadr(box)
              points = fig~>points
              pt = vbnConstrainPoint(start pt)
              axis = if(abs(vbnX(pt)-vbnX(start)) >=
                        abs(vbnY(pt)-vbnY(start)) then 'x else 'y)
              if(axis == 'x then
                sign = vbnSelectedSide(points selectedPoints 'x
                  (vbnX(ll)+vbnX(ur))/2.0
                  if(vbnX(start) >= (vbnX(ll)+vbnX(ur))/2.0 then 1 else -1))
                if(sign > 0 then ur = vbnPoint(vbnSnap(vbnX(ll)+value) vbnY(ur))
                else ll = vbnPoint(vbnSnap(vbnX(ur)-value) vbnY(ll)))
              else
                sign = vbnSelectedSide(points selectedPoints 'y
                  (vbnY(ll)+vbnY(ur))/2.0
                  if(vbnY(start) >= (vbnY(ll)+vbnY(ur))/2.0 then 1 else -1))
                if(sign > 0 then ur = vbnPoint(vbnX(ur) vbnSnap(vbnY(ll)+value))
                else ll = vbnPoint(vbnX(ll) vbnSnap(vbnY(ur)-value))))
              vbnPreviewObjects = append(vbnBoxLine(vbnPreviewSet list(ll ur))
                                        vbnPreviewObjects)
            )
          ))
      )
    )
  )
)

procedure(vbnDrawEdges(pt)
  let((hover first second a b p q dx dy mag midpoint projection)
    hover = when(pt vbnPickEdge(vbnWindow pt))
    when(hover
      vbnHoverObjects = cons(vbnLine(vbnHoverSet hover) vbnHoverObjects))
    foreach(edge vbnEdges
      vbnSelectedObjects = cons(vbnLine(vbnSelectedSet edge) vbnSelectedObjects))
    when(vbnEdges
      first = car(vbnEdges)
      if(cadr(vbnEdges) then
        second = cadr(vbnEdges)
        a = car(first) b = cadr(first)
        p = car(second) q = cadr(second)
        midpoint = vbnPoint((vbnX(a)+vbnX(b))/2.0
                            (vbnY(a)+vbnY(b))/2.0)
        dx = vbnX(b)-vbnX(a) dy = vbnY(b)-vbnY(a)
        mag = dx*dx+dy*dy
        projection = if(mag > 0.0 then
          (vbnX(p)+vbnX(q)-2*vbnX(midpoint))*dx/(2*mag) +
          (vbnY(p)+vbnY(q)-2*vbnY(midpoint))*dy/(2*mag)
          else 0.0)
        vbnArrow(midpoint
          vbnPoint((vbnX(p)+vbnX(q))/2.0-projection*dx
                   (vbnY(p)+vbnY(q))/2.0-projection*dy))
      else vbnArrow(car(first) cadr(first)))
    )
  )
)

procedure(vbnUpdateDisplay()
  let((pt screen view ll ur height origin labelText value)
    when(vbnActive && vbnWindow && vbnHilight
      pt = hiGetPoint(vbnWindow)
      screen = hiGetScreenPoint(vbnWindow)
      labelText = vbnDisplayText()
      value = vbnCurrentValue()
      when(pt && (!equal(pt vbnLastPoint) ||
                  !equal(screen vbnLastScreenPoint) || labelText != vbnLastText ||
                  !equal(value vbnLastValue) || !equal(vbnEdges vbnLastEdges) ||
                  vbnSnapMode() != vbnLastSnapMode)
        when(vbnHilightLabel geDeleteHilightObject(vbnHilightLabel))
        vbnClearObjects(vbnHoverObjects)
        vbnClearObjects(vbnSelectedObjects)
        vbnClearObjects(vbnPreviewObjects)
        vbnHoverObjects = nil vbnSelectedObjects = nil vbnPreviewObjects = nil
        view = hiGetViewBBox(vbnWindow)
        ll = car(view) ur = cadr(view)
        height = max(0.02 (vbnY(ur)-vbnY(ll))/35.0)
        origin = vbnPoint(vbnX(pt)+height/2.0 vbnY(pt)+height/2.0)
        vbnHilightLabel = geAddHilightLabel(vbnHilight origin labelText
          "lowerLeft" "R0" "stick" height nil)
        vbnLastPoint = pt
        vbnLastScreenPoint = screen
        vbnLastText = labelText
        vbnLastValue = value
        vbnLastEdges = vbnEdges
        vbnLastSnapMode = vbnSnapMode()
        vbnDrawEdges(pt)
        vbnDrawPreview(pt value)
        geRefreshWindow(vbnWindow)
      )
    )
  )
)

procedure(vbnTick()
  when(vbnActive
    if(member(vbnWindow hiGetWindowList()) &&
       hiGetCurrentWindow() == vbnWindow &&
       hiGetCurrentCmd(vbnWindow) == vbnCommand then
      vbnUpdateDisplay()
      hiRegTimer("vbnTick()" 2)
    else
      vbnStop()
    )
  )
)

procedure(vbnCaptureKey(key command)
  vbnSavedKeys = cons(list(key hiGetBindKey("Layout" key)) vbnSavedKeys)
  hiSetBindKey("Layout" key command)
)

procedure(vbnCaptureInput()
  let((i digit key)
    vbnSavedKeys = nil
    for(i 0 9
      digit = sprintf(nil "%d" i)
      key = sprintf(nil "<Key>%s EF" digit)
      vbnCaptureKey(key sprintf(nil "vbnDigit(\"%s\")" digit))
    )
    vbnCaptureKey("<Key>period EF" "vbnDigit(\".\")")
    vbnCaptureKey("<Key>BackSpace EF" "vbnBackspace()")
    vbnCaptureKey("<Key>Escape EF" "vbnEscape()")
    vbnCaptureKey("<Key>Return EF" "vbnConfirm()")
    vbnCaptureKey("<Key>KP_Enter EF" "vbnConfirm()")
    vbnCaptureKey("<Key>space EF" "vbnConfirm()")
    vbnCaptureKey("None<Btn1Down> EF" "vbnClick()")
  )
)

procedure(vbnReleaseInput()
  foreach(binding vbnSavedKeys
    hiSetBindKey("Layout" car(binding)
      if(cadr(binding) then cadr(binding) else ""))
  )
  vbnSavedKeys = nil
)

procedure(vbnStop()
  vbnActive = nil
  when(vbnHilight
    geDeleteHilightSet(vbnHilight)
    vbnHilight = nil
  )
  foreach(set list(vbnHoverSet vbnSelectedSet vbnPreviewSet)
    when(set geDeleteHilightSet(set)))
  vbnHoverSet = nil vbnSelectedSet = nil vbnPreviewSet = nil
  vbnHoverObjects = nil vbnSelectedObjects = nil vbnPreviewObjects = nil
  vbnHilightLabel = nil
  vbnReleaseInput()
  vbnWindow = nil
  vbnEdges = nil
  vbnNumber = nil
  vbnDigits = ""
  t
)

procedure(vbnStart(kind)
  let((cv lpp)
    vbnWindow = hiGetCurrentWindow()
    vbnCommand = hiGetCurrentCmd(vbnWindow)
    vbnForm = hiGetCurrentForm()
    vbnKind = kind
    vbnDigits = ""
    vbnNumber = nil
    vbnEdges = nil
    vbnLastPoint = nil
    vbnLastText = nil
    vbnLastValue = nil
    vbnLastEdges = nil
    vbnLastSnapMode = nil
    vbnLastScreenPoint = nil
    vbnPixelScale = nil
    vbnPixelScaleView = nil
    cv = geGetEditCellView(vbnWindow)
    lpp = leGetEntryLayer()
    when(cv && lpp
      vbnHilight = geCreateHilightSet(cv lpp)
      when(vbnHilight vbnHilight~>enable = t)
      vbnHoverSet = geCreateWindowHilightSet(vbnWindow "ge_glyph_yellow")
      vbnSelectedSet = geCreateWindowHilightSet(vbnWindow "ge_glyph_magenta")
      vbnPreviewSet = geCreateWindowHilightSet(vbnWindow "ge_glyph_magenta")
      foreach(set list(vbnHoverSet vbnSelectedSet vbnPreviewSet)
        when(set set~>enable = t))
    )
    vbnActive = t
    vbnCaptureInput()
    vbnUpdateDisplay()
    hiRegTimer("vbnTick()" 2)
    t
  )
)

procedure(vbnDigit(char)
  when(vbnActive
    when(vbnEdges
      vbnEdges = nil
      vbnNumber = nil
      vbnDigits = ""
    )
    when(char != "." || !rexMatchp("\\." vbnDigits)
      vbnDigits = strcat(vbnDigits char)
    )
    vbnUpdateDisplay()
  )
)

procedure(vbnBackspace()
  when(vbnActive
    if(vbnEdges then
      vbnEdges = nil
      vbnNumber = nil
    else
      when(strlen(vbnDigits) > 0
        vbnDigits = substring(vbnDigits 1 strlen(vbnDigits)-1)
      )
    )
    vbnUpdateDisplay()
  )
)

procedure(vbnEscape()
  when(vbnActive
    cond(
      (vbnEdges
        vbnEdges = nil
        vbnNumber = nil
        vbnDigits = ""
        vbnUpdateDisplay())
      (vbnDigits != ""
        vbnDigits = ""
        vbnUpdateDisplay())
      (t vbnStop())
    )
  )
)

procedure(vbnSelectEdge(edge)
  if(!vbnEdges || length(vbnEdges) >= 2 || equal(car(vbnEdges) edge) then
    vbnEdges = list(edge)
    vbnNumber = vbnEdgeLength(edge)
  else
    if(vbnParallel(car(vbnEdges) edge) then
      vbnNumber = vbnParallelDistance(car(vbnEdges) edge)
      vbnEdges = list(car(vbnEdges) edge)
    else
      vbnEdges = list(edge)
      vbnNumber = vbnEdgeLength(edge)
    )
  )
  vbnDigits = ""
  vbnUpdateDisplay()
  vbnNumber
)

procedure(vbnClick()
  let((pt edge)
    when(vbnActive
      pt = hiGetPoint(vbnWindow)
      when(pt
        edge = vbnPickEdge(vbnWindow pt)
        if(edge then vbnSelectEdge(edge)
        else when(vbnCurrentValue() vbnConfirm()))
      )
    )
  )
)

procedure(vbnEnteredStartPoint()
  let((points entry)
    points = hiGetCurrentEnterFunPoints()
    when(points
      entry = car(last(points))
      if(numberp(car(entry)) then entry else car(entry))
    )
  )
)

procedure(vbnSnapMode()
  let((field mode)
    field = when(vbnForm vbnForm~>segSnapMode)
    mode = when(field field~>value)
    if(mode then mode else "anyAngle")
  )
)

procedure(vbnConstrainPoint(start current)
  let((dx dy mode ax ay)
    dx = vbnX(current)-vbnX(start)
    dy = vbnY(current)-vbnY(start)
    ax = abs(dx) ay = abs(dy)
    mode = vbnSnapMode()
    cond(
      ((mode == "orthogonal" || mode == "horizontal" || mode == "vertical")
        if(mode == "horizontal" ||
           (mode == "orthogonal" && ax >= ay) then dy = 0.0
        else dx = 0.0))
      (mode == "diagonal"
        cond(
          (ay <= 0.4142135624*ax dy = 0.0)
          (ax <= 0.4142135624*ay dx = 0.0)
          (t
            if(ax <= ay then dx = if(dx < 0.0 then -ay else ay)
            else dy = if(dy < 0.0 then -ax else ax)))))
    )
    vbnPoint(vbnX(start)+dx vbnY(start)+dy)
  )
)

procedure(vbnDirection()
  let((start current dx dy magnitude)
    start = vbnEnteredStartPoint()
    current = hiGetPoint(vbnWindow)
    when(start && current
      current = vbnConstrainPoint(start current)
      dx = vbnX(current)-vbnX(start)
      dy = vbnY(current)-vbnY(start)
      magnitude = sqrt(dx*dx+dy*dy)
      when(magnitude > 0.0 list(dx/magnitude dy/magnitude))
    )
  )
)

procedure(vbnSetFormField(field value)
  field~>value = value
  when(field~>_callback && field~>_callback != ""
    evalstring(field~>_callback)
  )
)

procedure(vbnShiftSelectedPoints(points flags axis delta)
  if(points then
    cons(
      if(car(flags) then
        if(axis == 'x then
          vbnPoint(vbnSnap(vbnX(car(points))+delta) vbnY(car(points)))
          else vbnPoint(vbnX(car(points)) vbnSnap(vbnY(car(points))+delta)))
        else car(points))
      vbnShiftSelectedPoints(cdr(points) cdr(flags) axis delta))
    else nil)
)

procedure(vbnSelectedSide(points flags axis middle fallback)
  cond(
    ((!points || !flags) fallback)
    (car(flags)
      if(axis == 'x then
        if(vbnX(car(points)) >= middle then 1 else -1)
        else if(vbnY(car(points)) >= middle then 1 else -1)))
    (t vbnSelectedSide(cdr(points) cdr(flags) axis middle fallback))
  )
)

procedure(vbnApplyDistance(value)
  let((direction dx dy)
    direction = vbnDirection()
    if(!direction then
      warn("Numeric Assist: point from native Move/Stretch start to cursor before confirming.\n")
      nil
    else
      dx = vbnSnap(value*car(direction))
      dy = vbnSnap(value*cadr(direction))
      if(vbnCommand == "Move" then
        vbnSetFormField(vbnForm~>moveXField dx)
        vbnSetFormField(vbnForm~>moveYField dy)
        evalstring(vbnForm~>submitXY2~>_callback)
      else
        vbnSetFormField(vbnForm~>DeltaXField dx)
        vbnSetFormField(vbnForm~>DeltaYField dy)
        evalstring(vbnForm~>submitXY~>_callback)
      )
      t
    )
  )
)

procedure(vbnApplyLinearLength(fig selectedPoints current value)
  let((points fixed moving target targetX targetY newPoints)
    points = fig~>points
    if(car(selectedPoints) then
      moving = car(points)
      fixed = cadr(points)
    else
      moving = cadr(points)
      fixed = car(points)
    )
    target = vbnLinearTarget(fixed moving current value)
    if(!target then
      warn("Numeric Assist: selected line has zero length.\n")
      nil
    else
      targetX = vbnX(target)
      targetY = vbnY(target)
      vbnSetFormField(vbnForm~>DeltaXField targetX-vbnX(moving))
      vbnSetFormField(vbnForm~>DeltaYField targetY-vbnY(moving))
      evalstring(vbnForm~>submitXY~>_callback)
      ; Native Stretch can round relative deltas by a half grid.  Write the
      ; absolute target to the selected figure after it completes.
      when(dbIsId(fig)
        newPoints = if(car(selectedPoints) then
          list(vbnPoint(targetX targetY) fixed)
          else list(fixed vbnPoint(targetX targetY)))
        fig~>points = newPoints)
      t
    )
  )
)

procedure(vbnApplyLength(value)
  let((selection fig selectedPoints box ll ur start current axis sign delta targetBox originalPoints)
    selection = geGetSelSet(vbnWindow)
    fig = car(selection)
    start = vbnEnteredStartPoint()
    current = hiGetPoint(vbnWindow)
    selectedPoints = when(fig geGetSelSetFigPoint(fig))
    if(length(selection) != 1 || !fig || !start || !current ||
       !member(t selectedPoints) ||
       !member(nil selectedPoints) then
      warn("Numeric Assist: select one edge or endpoint with native Stretch before confirming length.\n")
      nil
    else if((fig~>objType == "ruler" || fig~>objType == "path") &&
            length(fig~>points) == 2 && length(selectedPoints) == 2 then
      vbnApplyLinearLength(fig selectedPoints current value)
    else
      box = fig~>bBox
      originalPoints = fig~>points
      ll = car(box) ur = cadr(box)
      current = vbnConstrainPoint(start current)
      axis = if(abs(vbnX(current)-vbnX(start)) >=
                abs(vbnY(current)-vbnY(start)) then 'x else 'y)
      if(axis == 'x then
        sign = vbnSelectedSide(originalPoints selectedPoints 'x
          (vbnX(ll)+vbnX(ur))/2.0
          if(vbnX(start) >= (vbnX(ll)+vbnX(ur))/2.0 then 1 else -1))
        delta = if(sign > 0 then vbnSnap(vbnX(ll)+value)-vbnX(ur)
                else vbnSnap(vbnX(ur)-value)-vbnX(ll))
        vbnSetFormField(vbnForm~>DeltaXField delta)
        vbnSetFormField(vbnForm~>DeltaYField 0.0)
        targetBox = if(sign > 0 then
          list(ll vbnPoint(vbnSnap(vbnX(ll)+value) vbnY(ur)))
          else list(vbnPoint(vbnSnap(vbnX(ur)-value) vbnY(ll)) ur))
      else
        sign = vbnSelectedSide(originalPoints selectedPoints 'y
          (vbnY(ll)+vbnY(ur))/2.0
          if(vbnY(start) >= (vbnY(ll)+vbnY(ur))/2.0 then 1 else -1))
        delta = if(sign > 0 then vbnSnap(vbnY(ll)+value)-vbnY(ur)
                else vbnSnap(vbnY(ur)-value)-vbnY(ll))
        vbnSetFormField(vbnForm~>DeltaXField 0.0)
        vbnSetFormField(vbnForm~>DeltaYField delta)
        targetBox = if(sign > 0 then
          list(ll vbnPoint(vbnX(ur) vbnSnap(vbnY(ll)+value)))
          else list(vbnPoint(vbnX(ll) vbnSnap(vbnY(ur)-value)) ur))
      )
      evalstring(vbnForm~>submitXY~>_callback)
      when(dbIsId(fig)
        cond(
          (fig~>objType == "rect" fig~>bBox = targetBox)
          (originalPoints
            fig~>points = vbnShiftSelectedPoints(originalPoints selectedPoints
                                                   axis delta))
        ))
      t
    ))
  )
)

procedure(vbnConfirm()
  let((value ok)
    value = vbnCurrentValue()
    if(!numberp(value) || value < 0.0 ||
       (vbnKind != 'distance && value == 0.0) then
      warn("Numeric Assist: enter a positive number.\n")
      nil
    else
      ok = cond(
        (vbnKind == 'width
          vbnSetFormField(vbnForm~>fixedWidthPaths t)
          vbnSetFormField(vbnForm~>pathWidth value)
          t)
        (vbnKind == 'length vbnApplyLength(value))
        (vbnKind == 'wire
          vbnSetFormField(vbnForm~>wireWidth value)
          t)
        (vbnKind == 'distance vbnApplyDistance(value))
      )
      when(ok vbnStop())
      ok
    )
  )
)

procedure(vbnHotkey(shift)
  let((win command kind form)
    when(vbnEnabled
    win = hiGetCurrentWindow()
    command = hiGetCurrentCmd(win)
    kind = cond(
      ((command == "Path") && !shift 'width)
      ((command == "Wire") && !shift 'wire)
      ((command == "Stretch") && !shift 'length)
      ((command == "Move") || ((command == "Stretch") && shift) 'distance)
      (t nil)
    )
    if(!kind then
      warn("Numeric Assist: start native Path, Wire, Stretch, or Move first.\n")
      nil
    else
      if(vbnActive && win == vbnWindow && kind == vbnKind then
        when(vbnCurrentValue() vbnConfirm())
      else
        when(vbnActive vbnStop())
        form = hiGetCurrentForm()
        if(!form ||
           (command == "Path" && form~>_formName != "Create Path") ||
           (command == "Wire" && form~>_formName != "Create Wire") ||
           (command == "Stretch" && form~>_formName != "Stretch") ||
           (command == "Move" && form~>_formName != "Move") then
          warn("Numeric Assist: native command form is unavailable.\n")
          nil
        else vbnStart(kind))
      )
    )
    )
  )
)

procedure(vbnToggle()
  vbnEnabled = !vbnEnabled
  when(!vbnEnabled && vbnActive vbnStop())
  when(vbnAction hiSetActionChecked(vbnAction vbnEnabled nil))
  printf("Numeric Assist %s\n" if(vbnEnabled then "on" else "off"))
  vbnEnabled
)

; Kept as a no-op for callbacks queued by revisions loaded before the
; generation-scoped timer was introduced.
procedure(vbnToolbarTick() nil)

procedure(vbnToolbarLoop(generation)
  let((cv)
   when(vbnInstalled && generation == vbnToolbarGeneration
    foreach(win hiGetWindowList()
      cv = geGetWindowCellView(win)
      when(cv && cv~>viewName == "layout" &&
           !member(win vbnToolbarWindows)
        when(hiPlaceToolbar(win vbnToolbar 'top)
          vbnToolbarWindows = cons(win vbnToolbarWindows)))
    )
    hiRegTimer(sprintf(nil "vbnToolbarLoop(%d)" generation) 20)
   ))
)

procedure(vbnInstall()
  unless(vbnInstalled
    vbnMainOld = hiGetBindKey("Layout" "<Key>j EF")
    vbnShiftOld = hiGetBindKey("Layout" "Shift<Key>j EF")
    hiSetBindKey("Layout" "<Key>j EF" "vbnHotkey(nil)")
    hiSetBindKey("Layout" "Shift<Key>j EF" "vbnHotkey(t)")
    vbnAction = hiCreateAction(?name 'vbnToggleAction
      ?iconText "Numeric J" ?toolTip "Toggle Numeric Assist (J / Shift+J)"
      ?callback "vbnToggle()" ?checkable t ?checked t)
    vbnToolbar = hiCreateToolbar(?name 'vbnToolbar
      ?title "Numeric Assist" ?toolButtonStyle 'textOnly
      ?items list(vbnAction))
    vbnInstalled = t
    vbnToolbarLoop(vbnToolbarGeneration)
  )
  vbnInstalled
)

procedure(vbnUninstall()
  when(vbnActive vbnStop())
  when(vbnInstalled
    foreach(win vbnToolbarWindows
      when(member(win hiGetWindowList()) hiDeleteToolbar(win 'vbnToolbar)))
    vbnToolbarWindows = nil
    hiSetBindKey("Layout" "<Key>j EF"
      if(vbnMainOld then vbnMainOld else ""))
    hiSetBindKey("Layout" "Shift<Key>j EF"
      if(vbnShiftOld then vbnShiftOld else ""))
    vbnInstalled = nil
  )
  t
)

vbnInstall()
