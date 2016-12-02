from tilesets.models import Tileset
from tilesets.serializers import TilesetSerializer
from tilesets.serializers import UserSerializer
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework import permissions
from tilesets.permissions import IsOwnerOrReadOnly
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.decorators import api_view, permission_classes
from tilesets.permissions import IsOwnerOrReadOnly
from django.views.decorators.gzip import gzip_page
import base64
import os
import os.path as op
import h5py
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
import numpy as np
import getter as hgg
from tiles import makeTile
from itertools import chain
from django.db.models import Q
import clodius.hdf_tiles as hdft
import urllib
import json
import cooler
import multiprocessing as mp

global mats
mats = {}


def makeMats(dset):
    f = h5py.File(dset, 'r')
    mats[dset] = [f, hgg.getInfo(dset)]


def makeUnaryDict(hargs, queryset):
    odict = {}

    prea = hargs.split('.')
    prea[0] = prea[0]
    numerics = prea[1:4]
    nuuid = prea[0]
    tile_zoom_pos = map(lambda x: int(x), numerics)
    cooler = queryset.filter(uuid=nuuid).first()
    odict = {}

    print "tile_zoom_pos:", tile_zoom_pos

    if mats.has_key(cooler.processed_file) == False:
        makeMats(cooler.processed_file)

    tileset_file_and_info = mats[cooler.processed_file]

    if tile_zoom_pos[0] > tileset_file_and_info[1]['max_zoom']:
        # we don't have enough zoom levels
        return None
    if tile_zoom_pos[1] >= 2 ** tile_zoom_pos[0]:
        # tile is out of bounds
        return None
    if tile_zoom_pos[2] >= 2 ** tile_zoom_pos[0]:
        # tile is out of bounds
        return None

    tile = makeTile(tile_zoom_pos[0], tile_zoom_pos[1], tile_zoom_pos[2],
                                  mats[cooler.processed_file])
    odict["min_value"] = float(np.min(tile))
    odict["max_value"] = float(np.max(tile))
    odict['dense'] = base64.b64encode(tile)

    return [odict, hargs]


def parallelize(elems):
    queryset = Tileset.objects.all()
    prea = elems.split('.')
    numerics = prea[1:3]
    nuuid = prea[0]
    argsa = map(lambda x: int(x), numerics)
    cooler = queryset.filter(uuid=nuuid).first()
    if cooler.file_type == "hitile":
        '''
        print("processed_file:", cooler.processed_file)
        print("exists:", op.exists(cooler.processed_file))
        print("int(argsa[0])", int(argsa[0]), int(argsa[1]))
        '''
        dense = hdft.get_data(h5py.File(cooler.processed_file), int(argsa[0]),
                          int(argsa[1]))
        minv = min(dense)
        maxv = max(dense)

        d = {}
        #d["min_value"] = minv
        #d["max_value"] = maxv
        d["dense"] = base64.b64encode(dense)

        return (nuuid, d)
    elif cooler.file_type == "elastic_search":
        prea = elems.split('.')
        prea[0] = prea[0]
        numerics = prea[1:4]
        response = urllib.urlopen(
            cooler.processed_file + '/' + numerics[0] + '.' + numerics[
                1] + '.' + numerics[2])
        od[elems] = json.loads(response.read())["_source"]["tile_value"]
        return od
    else:
        ud = makeUnaryDict(elems, queryset)
        if ud is None:
            return None
        return (ud[1], ud[0])
        # od[ud[1]] = ud[0]


@method_decorator(gzip_page, name='dispatch')
class TilesetsViewSet(viewsets.ModelViewSet):
    """
    Tilesets
    """

    def get_queryset(self):

        # debug NOT SECURE
        queryset = super(TilesetsViewSet, self).get_queryset()
        return queryset

        # secure production
        return Tileset.objects.none()

    queryset = Tileset.objects.all()
    serializer_class = TilesetSerializer
    # permission_classes = (IsOwnerOrReadOnly,)
    lookup_field = 'uuid'

    @detail_route(renderer_classes=[renderers.StaticHTMLRenderer])
    def render(self, request, *arg, **kwargs):
        global mats
        # queryset=Tileset.objects.all()
        hargs = request.GET.getlist("d")
        # with ProcessPoolExecutor() as executor:
        #	res = executor.map(parallelize, hargs)
        '''
        p = mp.Pool(4)
        res = p.map(parallelize, hargs)
        '''

        # create a set so that we don't fetch the same tile multiple times
        hargs_set = set(hargs)
        res = map(parallelize, hargs_set)
        d = {}
        for item in res:
            if item is None:
                continue
            d[item[0]] = item[1]
        return JsonResponse(d, safe=False)

    @detail_route(renderer_classes=[renderers.StaticHTMLRenderer])
    def tileset_info(self, request, *args, **kwargs):
        global mats
        queryset = Tileset.objects.all()
        hargs = request.GET.getlist("d")
        d = {}
        for elems in hargs:
            cooler = queryset.filter(uuid=elems).first()
            if cooler.file_type == "hitile":
                d[elems] = hdft.get_tileset_info(
                    h5py.File(cooler.processed_file))
            elif cooler.file_type == "elastic_search":
                response = urllib.urlopen(
                    cooler.processed_file + "/tileset_info")
                d[elems] = json.loads(response.read())
            else:
                dsetname = queryset.filter(uuid=elems).first().processed_file
                if mats.has_key(dsetname) == False:
                    makeMats(dsetname)
                d[elems] = mats[dsetname][1]
        return JsonResponse(d, safe=False)


        # info should be a dictionary describing the processed file
        # e.g. dimensions, min_value, max_value, histogram of values

    @detail_route(renderer_classes=[renderers.StaticHTMLRenderer])
    def generate_tiles(self, request, *args, **kwargs):
        cooler = self.get_object()
        serializer = TilesetSerializer(cooler, data=request.data)
        cooler.rawfile_in_db = True
        idv = cooler.id
        # os.system("source activate snakes")
        os.system("wget " + cooler.url)
        urlval = cooler.url.split('/')[-1]
        os.system("mv " + str(urlval) + " " + str(urlval).lower())
        urlval = urlval.lower()
        os.system("python recursive_agg_onefile.py" + urlval)
        cooler.processed_file = '.'.join(
            urlval.split('.')[:-1]) + ".multires.cool"
        cooler.processed = True
        cooler.save()
        return HttpResponseRedirect("/tilesets/")

    def perform_create(self, serializer):
        serializer.save()
        return HttpResponse("test")