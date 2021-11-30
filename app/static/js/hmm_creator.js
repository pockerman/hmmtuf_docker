$(function () {
  var state = 0;
  var mcom = 0;

  $("#add_state").on("click", function () {


    if (state < 6) {

      var remove = $(document).find(".closebtn");
      if(remove.length){remove.hide()};
      var s = state + 1;
      $("#state-group").append(
        `
        <fieldset class="mb-2 p-2" name="State[${s}]">
        <legend>State ${s}</legend>
        <div class="closebtn row"><button type="button" class="btn btn-small btn-circle pull-right remove_St btn-danger"><i class="fas fa-times"></i></button></div>
        <div class="state mb-2 mt-2">
        <div class="form-group mb-2">
        <label for="st_name">Name of state:</label>
        <input type="text" name="State[${s}][st_name]" class="form-control">
        </div>
        <div class="row p-2">
        <button type="button" class="btn btn-light single-component col-4 form-control m-2">Single Component</button>
        <button type="button" class="btn btn-light mix-component form-control col-4 form-control m-2">Mixture Component</button>
        <input type="text"  name="State[${s}][com_type]" hidden id="com_type${s}" class="com_type form-control">
        </div>
        <div class="component-div">
        
        </div>
        <input type="number" class="s_no" hidden value="${s}">
        </div>
        </fieldset>
      `
      );
      if (state + 1 > 1) {
        $(".prob").show();
      }

      state++;

      if ($("#IPV-group").is(":visible")) {
        $("#add_IPV").click();
      }
      if ($("#TPM-group").is(":visible")) {
        $("#add_TPM").click();
      }
    } else {
      alert("You can add only 6 states");
    }
  });

  // remove state handler
 $(document).on("click",".remove_St" , function (){

    var stToRemove= $(this).parent().parent();
    var PreviousState= stToRemove.prev();

    PreviousState.find('.closebtn').show();

    stToRemove.remove();
    --state;
    
    if (state === 1) {
        $(".prob").hide();
        $("#IPV-group").empty();
        $("#TPM-group").empty();
        $("#IPV-group").hide();
        $("#TPM-group").hide();
      }
    if ($("#IPV-group").is(":visible")) {
      $("#add_IPV").click();
    }
    if ($("#TPM-group").is(":visible")) {
      $("#add_TPM").click();
    }


 });
  //

  // Single Component Structure
  $(document).on("click", ".single-component", function () {
    $(this).parent().find(".com_type").val("SingleComponent");
    var p = $(this).parent().parent();
    var sno = p.find(".s_no").val();
    var elem = p.find(".component-div");
    if (elem.is(":visible")) {
      elem.empty();
      elem.hide();
      $(this).parent().find(".mix-component").attr("disabled", false);
    }
    elem.append(`  
    <div class="componentItem">
    <div class="form-group">
        <div class="row p-2">
            <input type="number" class="s_no" hidden  value=${sno}>
            <input type="text" class = "dist" hidden name="State[${sno}][distribution]">
            <button type="button" class="btn btn-light normal-com col-4 form-control m-2">Normal</button>
            <button type="button" class="btn btn-light uniform-com form-control col-4 form-control m-2">Uniform</button>
        </div>

        <div class="single-com-view"></div>
    </div>  
    </div>
    `);
    elem.show();
    $(this).attr("disabled", true);
  });

  $(document).on("click", ".normal-com", function () {
    var sno = $(this).parent().find(".s_no").val();
    $(this).parent().find(".dist").val("Normal");
    var elem = $(this).parent().parent().find(".single-com-view");
    if (elem.is(":visible")) {
      elem.empty();
      elem.hide();
      $(this).parent().find(".uniform-com").attr("disabled", false);
    }
    elem.append(`
        <div class="row mb-2">
            <div class="col-6">
                <div class ="control-group">
                    <label for="single_com_m1">WGA Mean</label>
                    <input type="number" step="0.1" min="0.00" class="form-control" name="State[${sno}][single_com_m1]" >
                </div>
            </div>
            <div class="col-6">
                <div class ="control-group">
                    <label for="single_com_m2">No WGA Mean</label>
                    <input type="number" step="0.1" min="0.00" class="form-control" name="State[${sno}][single_com_m2]" >
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-6">
            <div class="form-group">
            <label for="variant">WGA Variance:</label>
            <input type="number" step="0.1" min="0.00" class="form-control mb-2" name="State[${sno}][single_com_v1]">
            </div>
            </div>
            <div class="col-6">

            <div class="form-group">
            <label for="variant">No WGA Variance:</label>
            <input type="number" step="0.1" min="0.00" class="form-control mb-2" name="State[${sno}][single_com_v2]">
            </div>

            </div>
        </div>
    `);
    elem.show();
    $(this).attr("disabled", true);
  });

  $(document).on("click", ".uniform-com", function () {
    var elem = $(this).parent().parent().find(".single-com-view");
    var sno = $(this).parent().find(".s_no").val();
    $(this).parent().find(".dist").val("Uniform");
    if (elem.is(":visible")) {
      elem.empty();
      elem.hide();
      $(this).parent().find(".normal-com").attr("disabled", false);
    }

    elem.append(`
        <div class="form-group">
        <div class="row">
            <div class="col-6">
                <div class ="control-group">
                    <label for="single_com_l1">WGA Lower</label>
                    <input type="number" step="0.1" min="0.00" class="form-control" name="State[${sno}][single_com_l1]" >
                </div>
            </div>
            <div class="col-6">
                <div class ="control-group">
                    <label for="single_com_l2">No WGA Lower</label>
                    <input type="number" step="0.1" min="0.00" class="form-control" name="State[${sno}][single_com_l2]" >
                </div>
            </div>
        </div>
        <div class="row">
        <div class="col-6">
            <div class ="control-group">
                <label for="single_com_u1">WGA Upper</label>
                <input type="number" step="0.1" min="0.00" class="form-control" name="State[${sno}][single_com_u1]" >
            </div>
        </div>
        <div class="col-6">
            <div class ="control-group">
                <label for="single_com_u2">No WGA Upper</label>
                <input type="number" step="0.1" min="0.00" class="form-control" name="State[${sno}][single_com_u2]" >
            </div>
        </div>
    </div>
    </div>
    
    `);
    elem.show();
    $(this).attr("disabled", true);
  });

  // Mixture Componet Strucutre
  $(document).on("click", ".mix-component", function () {
    mcom=0;
    $(this).parent().find(".com_type").val("MixtureComponent");
    var elem = $(this).parent().parent().find(".component-div");
    if (elem.is(":visible")) {
      elem.empty();
      elem.hide();
      $(this).parent().find(".single-component").attr("disabled", false);
    }
    elem.append(`
    
           <button type="button" class="btn btn-light add_M_com col-4 form-control m-2">Add Component</button>
           <div class="componentGroup" name="components[]"></div>
           <fieldset class="weightgroup p-2" name="weights[]"><legend>Weights:</legend>
                
           </fieldset>
        `);
    elem.show();
    $(this).attr("disabled", true);
  });

  $(document).on("click", ".add_M_com", function () {
    var elem = $(this).parent().find(".componentGroup");
    var wight = $(this).parent().find(".weightgroup");
    var p = $(this).parent().parent();
    var sno = p.find(".s_no").val();
    elem.append(`  
    <div class="componentItem mb-2">
    <div class="form-group">
        <div class="row p-2">
            <input type="number" class="s_no" hidden  value=${sno}>
            <input type="number" class="c_no" hidden  value=${mcom}>
            <input type="text" class = "dist" hidden name="State[${sno}]components[${mcom}][distribution]">
            <button type="button" class="btn btn-light mnormal-com col-4 form-control m-2">Normal</button>
            <button type="button" class="btn btn-light muniform-com form-control col-4 form-control m-2">Uniform</button>
        </div>
        <div class="msingle-com-view"></div>  
    </div>  
    </div>
    `);

    wight.append(`
                <input type="number" step="0.1"  placeholder="Component ${mcom+1}" class="m-2" name="State[${sno}]weights[${mcom}][M_com_weight]">`)
    mcom++;
    elem.show();
  });

  $(document).on("click", ".muniform-com", function () {
    var elem = $(this).parent().parent().find(".msingle-com-view");
    var sno = $(this).parent().find(".s_no").val();
    var cno = $(this).parent().find(".c_no").val();
    $(this).parent().find(".dist").val("Uniform");
    if (elem.is(":visible")) {
      elem.empty();
      elem.hide();
      $(this).parent().find(".mnormal-com").attr("disabled", false);
    }

    elem.append(`
        <div class="form-group">
        <div class="row">
            <div class="col-6">
                <div class ="control-group">
                    <label for="single_com_l1">WGA Lower</label>
                    <input type="number" step="0.1" min="0.00" class="form-control" name="State[${sno}]components[${cno}][single_com_l1]" >
                </div>
            </div>
            <div class="col-6">
                <div class ="control-group">
                    <label for="single_com_l2">No WGA Lower</label>
                    <input type="number" step="0.1" min="0.00" class="form-control" name="State[${sno}]components[${cno}][single_com_l2]" >
                </div>
            </div>
        </div>
        <div class="row">
        <div class="col-6">
            <div class ="control-group">
                <label for="single_com_u1">WGA Upper</label>
                <input type="number" step="0.1" min="0.00" class="form-control" name="State[${sno}]components[${cno}][single_com_u1]" >
            </div>
        </div>
        <div class="col-6">
            <div class ="control-group">
                <label for="single_com_u2">No WGA Upper</label>
                <input type="number" step="0.1" min="0.00" class="form-control" name="State[${sno}]components[${cno}][single_com_u2]" >
            </div>
        </div>
    </div>
    </div>
    
    `);
    elem.show();
    $(this).attr("disabled", true);
  });

  $(document).on("click", ".mnormal-com", function () {
    var sno = $(this).parent().find(".s_no").val();
    var cno = $(this).parent().find(".c_no").val();
    $(this).parent().find(".dist").val("Normal");
    var elem = $(this).parent().parent().find(".msingle-com-view");
    if (elem.is(":visible")) {
      elem.empty();
      elem.hide();
      $(this).parent().find(".muniform-com").attr("disabled", false);
    }
    elem.append(`
        <div class="row mb-2">
            <div class="col-6">
                <div class ="control-group">
                    <label for="single_com_m1">WGA Mean</label>
                    <input type="number" step="0.1" min="0.00" class="form-control" name="State[${sno}]components[${cno}][single_com_m1]" >
                </div>
            </div>
            <div class="col-6">
                <div class ="control-group">
                    <label for="single_com_m2">No WGA Mean</label>
                    <input type="number" step="0.1" min="0.00"  class="form-control" name="State[${sno}]components[${cno}][single_com_m2]" >
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-6">
                <div class="form-group">
                    <label for="variant">WGA Variance:</label>
                    <input type="number" step="0.1" min="0.00" class="form-control mb-2" name="State[${sno}]components[${cno}][single_com_v1]">
                </div>
            </div>
            <div class="col-6">
                  
            <div class="form-group">
                <label for="variant">No WGA Variance:</label>
                <input type="number" step="0.1" min="0.00" class="form-control mb-2" name="State[${sno}]components[${cno}][single_com_v2]">
            </div>

            </div>
        </div>
    `);
    elem.show();
    $(this).attr("disabled", true);
  });


  // Mixture Component Structure End

  $(document).on("click", "#add_IPV", function () {
    $("#IPV-group").show();

    var elem = $(this).parent().find("#IPV-group").find(".field-group");

    elem.find(".ipt-field").remove();

    for (var i = 0; i < state; i++) {
      elem.append(
        `<input type="number" class="ipt-field m-2" placeholder="Enter initial probabilty for state ${
          i + 1
        }" step="0.1" min="0.0" >`
      );
    }
  });

  $(document).on("change", ".ipt-field", function () {
    let ipvarr = [];
    ipvarr = $(".ipt-field")
      .map(function () {
        return this.value;
      })
      .get();

    var s = sum(ipvarr);
    var ele = document.getElementById("IPV-Value");
    if (s != 1) {
      $("#error").show();
      ele.value = "";
    } else if (s == 1) {
      $("#error").hide();
      ele.value = "";
      ele.value = ipvarr.join(",");
    }
  });

  $(document).on("click", "#add_TPM", function () {
    $("#TPM-group").show();
    var elem = $(this).parent().find("#TPM-group").find(".st-group");
    elem.find(".iptm-field").remove();
    for (var i = 0; i < state; i++) {
      elem.append(`
            
            <fieldset class="iptm-field p-2 sb-field">
                <legend class="sb-field-legend">State ${i + 1}</legend>
                <div class="mt-group p-2 row"></div>
                <div class="err" style="display:none"><small class="text-danger">Sum of all values should be 1</small></div>
                <input type="text" name="State_M[${i+1}][tpm]" id="tpm${
                  i + 1
                }" class="st-m form-control">
            </fieldset>
           
        `);

        console.log(state);
    }

    var child = elem.find(".iptm-field").find(".mt-group");

    for (var j = 0; j < state; j++) {
      child.append(
        `<input type="number" class="tm-field m-2" placeholder="Enter value for state ${
          j + 1
        }" step="0.1" min="0.0" >`
      );
    }
  });

  $(document).on("change", ".tm-field", function () {
    var parent = $(this).parent();
    let ipvarr = [];
    var inp = parent.parent();
    var index = inp.index();
    index = index + 1;
    var elem = document.getElementById("tpm" + index);
    ipvarr = parent
      .find(".tm-field")
      .map(function () {
        return this.value;
      })
      .get();

    var s = sum(ipvarr);

    if (s != 1) {
      parent.next(".err").show();
      elem.value = "";
    } else {
      parent.next(".err").hide();
      elem.value = "";
      elem.value = ipvarr.join(",");
    }
  });

  function sum(a) {
    return (a.length && parseFloat(a[0]) + sum(a.slice(1))) || 0;
  }
});
